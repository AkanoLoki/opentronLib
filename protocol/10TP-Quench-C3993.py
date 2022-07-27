from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from opentrons import protocol_api
import opentrons
# metadata
metadata = {
    'protocolName': '10-timepoint Quenching Assay',
    'author': 'Lux <lux011@brandeis.edu>',
    'description': 'Prototype protocol to prepare, start, taketimepoints and quench into a Corning 3993 96 well fluorescence microplate. Adapted from JYChow@NUS',
    'apiLevel': '2.12'}

# GLOBAL VARIABLE DEFINITION

OT2_DECK_SLOTS = 11  # Number of available deck slots in a OT-2 robot

# DATACLASS OF LABWARE DEFINITIONS


# Actual script below


def run(protocol: protocol_api.ProtocolContext):
    # ----------------  EQUIPMENT AND LABWARES  ----------------

    # Labware list on deck
    #   10      11      Trash   BACK
    #   7       8       9
    #   4       5       6
    #   1       2       3       FRONT

    # ----------------  LABWARE INITIALIZATION  ----------------

    # Readability names for labwares
    # OPENTRONS:

    # tipR_20
    tipR_300_1: protocol_api.labware.Labware = protocol.load_labware(
        'opentrons_96_tiprack_300ul', 9)
    tipR_300_2: protocol_api.labware.Labware = protocol.load_labware(
        'opentrons_96_tiprack_300ul', 10)
    tipR_300_3: protocol_api.labware.Labware = protocol.load_labware(
        'opentrons_96_tiprack_300ul', 11)
    # tipR_1000_1
    # tipR_20F
    # tipR_300F
    # tipR_1000F

    # tubeR_24xEpp
    tubeR_6x15_4x50: protocol_api.labware.Labware = protocol.load_labware(
        'opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', 4)

    # tubeR_15x15
    # tubeR_6x50

    # aluB_24w
    # aluB_96w
    # aluB_flat

    # CORNING:
    microP96_C3694: protocol_api.labware.Labware = protocol.load_labware(
        'corning_96_wellplate_190ul', 1)

    # THERMO SCI NUNC
    nuncP96_1mL: protocol_api.labware.Labware = protocol.load_labware(
        'thermoscientificnunc_96_wellplate_1300ul', 6)

    # ----------------  BUFFER SETUP            ----------------

    rBuf = tubeR_6x15_4x50.wells_by_name()['A1']
    qBuf = tubeR_6x15_4x50.wells_by_name()['A2']
    lysate = tubeR_6x15_4x50.wells_by_name()['B1']
    lysBuf = tubeR_6x15_4x50.wells_by_name()['C1']

    # ----------------  END OF BUFFER SETUP     ----------------
    # ----------------  EMPTY VESSEL SETUP      ----------------
    # substr = nuncP96_2mL.wells_by_name()['B2']
    # subBuf = tubeR_6x15_4x50.wells_by_name()['C2']
    rxnCol: list[protocol_api.labware.Well] = nuncP96_1mL.columns()[0]
    substrCol: list[protocol_api.labware.Well] = nuncP96_1mL.columns()[1]

    # ----------------  END OF EMPTY VESSEL SETUP   ------------
    # ----------------  RXN WELL SETUP          ----------------

    rxnWells = [
        (nuncP96_1mL, rxnCol[0], 'A1 E+ S+ rep1'),
        (nuncP96_1mL, rxnCol[1], 'B1 E+ S+ rep2'),
        (nuncP96_1mL, rxnCol[2], 'C1 E+ S+ rep3'),
        (nuncP96_1mL, rxnCol[3], 'D1 E+ S- rep1'),
        (nuncP96_1mL, rxnCol[4], 'E1 E+ S- rep2'),
        (nuncP96_1mL, rxnCol[5], 'F1 E- S+ rep1'),
        (nuncP96_1mL, rxnCol[6], 'G1 E- S+ rep2'),
        (nuncP96_1mL, rxnCol[7], 'H1 E- S- rep1')
    ]

    substrateWells = [
        (nuncP96_1mL, substrCol[0], 'A2 10uM Sub'),
        (nuncP96_1mL, substrCol[1], 'B2 10uM Sub'),
        (nuncP96_1mL, substrCol[2], 'C2 10uM Sub'),
        (nuncP96_1mL, substrCol[3], 'D2 10% DMSO'),
        (nuncP96_1mL, substrCol[4], 'E2 10% DMSO'),
        (nuncP96_1mL, substrCol[5], 'F2 10uM Sub'),
        (nuncP96_1mL, substrCol[6], 'G2 10uM Sub'),
        (nuncP96_1mL, substrCol[7], 'H2 10% DMSO')
    ]
    # ----------------  END OF RXN WELL SETUP   ----------------
    # ----------------  END OF LABWARE INIT.    ----------------
    # ----------------  PIPETTE INITIALIZATION  ----------------

    # Load Pipettes
    p300s = protocol.load_instrument(
        'p300_single_gen2', 'left', [tipR_300_3])

    p300m = protocol.load_instrument(
        'p300_multi_gen2', 'right', [tipR_300_1, tipR_300_2])

    # Initialize flow rate (faster than default)
    p300s.flow_rate.aspirate = 100
    p300s.flow_rate.dispense = 100

    p300m.flow_rate.aspirate = 100
    p300m.flow_rate.dispense = 100

    # ----------------  END OF PIPETTE INIT.    ----------------
    # ----------------  END OF EQUIPMENT AND LABWARES   --------
    # ----------------  START OF PROGRAM        ----------------

    protocol.pause('Please confirm deck setup. Resume to start sequence.')

    # Fill C3694 Well A1-H10 w/ 25uL ea. quenching buffer, blow out last 10uL back into tube
    p300s.pick_up_tip()
    for col in range(10):
        # Aspirate each column 1-10
        p300s.aspirate(210, qBuf, 0.5)
        for row in range(8):
            # Pipette each row of column A-H 25uL
            p300s.dispense(25, microP96_C3694.columns()[col][row])
        # Blow out rest in tip
        p300s.blow_out(qBuf)
    p300s.drop_tip()

    # Prepare 8x 30uL lysate/lysis buffer + 240uL rxn buffer reaction mix w/o substrate

    # Lysate first
    for row in range(8):
        # Pipette each row of column 1 A-H 30uL according to E+ or E- in well desc
        if 'E+' in rxnWells[row][2]:
            p300s.transfer(30, lysate, rxnWells[row][1])
        else:
            p300s.transfer(30, lysBuf, rxnWells[row][1])

    # Rxn buffer acidification of lysate
    # Pipette 240uL of reaction buffer in each well A1-H1
    p300s.transfer(30, rBuf, rxnWells[0][0].columns_by_name()[
                   '1'], new_tip='once')

    # Pause before starting rxn
    protocol.pause(
        'Check if mixture and plate are ready. Resuming will start pipetting substrate.')

    # Add substrates
    p300m.pick_up_tip()
    p300m.transfer(30, substrateWells[0][1],
                   rxnWells[0][1], new_tip='never')
    p300m.mix(5, 150)
    p300m.drop_tip()
    # Timepoint 1-10
    delayTimes = [30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0]
    for tp in range(10):
        # delay first
        protocol.delay(delayTimes[tp])
        # transfer to C3694
        p300m.transfer(25, rxnWells[0][1],
                       microP96_C3694.columns()[tp][0], True)

    # Finalizing cleanup
    if p300m.has_tip:
        p300m.drop_tip()
    if p300s.has_tip:
        p300s.drop_tip()
    protocol.pause('Sequence complete.')
