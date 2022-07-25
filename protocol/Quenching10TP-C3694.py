from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from opentrons import protocol_api
import opentrons
# metadata
metadata = {
    'protocolName': '10-timepoint Quenching Assay',
    'author': 'Lux <lux011@brandeis.edu>',
    'description': 'Prototype protocol to prepare, start, taketimepoints and quench into a Corning 3694 96 well fluorescence microplate. Adapted from JYChow@NUS',
    'apiLevel': '2.12'}

# GLOBAL VARIABLE DEFINITION

# For tip disposal
TO_TRASH = 'trash'
TO_RACK = 'rack'
TO_DEF = 'default'

OT2_DECK_SLOTS = 11  # Number of available deck slots in a OT-2 robot

# DATACLASS OF LABWARE DEFINITIONS


@dataclass
class LDef:
    slot: int
    name: str = ''
    used: bool = False


@dataclass
class PDef:
    mount: str
    name: str = ''
    used: bool = False


@dataclass
class WDef:
    plate: protocol_api.labware.Labware
    well: protocol_api.labware.Well
    desc: str = ''

# Actual script below


def run(protocol: protocol_api.ProtocolContext):

    # ----------------  RUN VARAIBLES           ----------------
    plateCol = 12  # Number of columns in 96-well plate, in triplicates of 3, 6, 9 or 12

    # Default used tip discarding method: TO_TRASH or TO_RACK
    defaultTipDiscardDest = TO_TRASH
    # defaultTipDiscardDest = TO_RACK

    # ----------------  END OF RUN VARAIBLES    ----------------

    # ----------------  EQUIPMENT AND LABWARES  ----------------

    # Labware list on deck
    #   10      11      Trash   BACK
    #   7       8       9
    #   4       5       6
    #   1       2       3       FRONT

    deckLabware = [
        LDef(1, 'corning_96_wellplate_190ul', True),
        LDef(2, '', False),
        LDef(3, '', False),
        LDef(4, 'opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', True),
        LDef(5, 'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', False),
        LDef(6, 'thermoscientificnunc_96_wellplate_2000ul', True),
        LDef(7, '', False),
        LDef(8, '', False),
        LDef(9, 'opentrons_96_tiprack_300ul', True),
        LDef(10, 'opentrons_96_tiprack_300ul', True),
        LDef(11, 'opentrons_96_tiprack_300ul', True),
    ]

    # ----------------  LABWARE INITIALIZATION  ----------------

    deckRefs = []
    deckRefs.append("\0")
    for i in range(len(deckLabware)):
        if(deckLabware[i].used):
            deckRefs.append(protocol.load_labware(
                deckLabware[i].name, deckLabware[i].slot))
        else:
            deckRefs.append("\0")

    # Readability names for labwares
    # OPENTRONS:

    # tipR_20
    tipR_300_1: protocol_api.labware.Labware = deckRefs[9]
    tipR_300_2: protocol_api.labware.Labware = deckRefs[10]
    tipR_300_3: protocol_api.labware.Labware = deckRefs[11]
    # tipR_1000_1
    # tipR_20F
    # tipR_300F
    # tipR_1000F

    # tubeR_24xEpp = deckRefs[5]
    tubeR_6x15_4x50: protocol_api.labware.Labware = deckRefs[4]
    # tubeR_15x15
    # tubeR_6x50

    # aluB_24w
    # aluB_96w
    # aluB_flat

    # CORNING:
    microP96_C3694: protocol_api.labware.Labware = deckRefs[1]

    # THERMO SCI NUNC
    nuncP96_2mL: protocol_api.labware.Labware = deckRefs[6]

    # ----------------  BUFFER SETUP            ----------------

    rBuf = tubeR_6x15_4x50.wells_by_name()['A1']
    qBuf = tubeR_6x15_4x50.wells_by_name()['A2']
    lysate = tubeR_6x15_4x50.wells_by_name()['B1']
    lysBuf = tubeR_6x15_4x50.wells_by_name()['C1']

    # substr = nuncP96_2mL.wells_by_name()['B2']
    # subBuf = tubeR_6x15_4x50.wells_by_name()['C2']
    substrCol = nuncP96_2mL

    # ----------------  END OF BUFFER SETUP     ----------------
    # ----------------  RXN WELL SETUP          ----------------

    rxnWells = [
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['A1'], 'A1 E+ S+ rep1'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['B1'], 'B1 E+ S+ rep2'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['C1'], 'C1 E+ S+ rep3'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['D1'], 'D1 E+ S- rep1'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['E1'], 'E1 E+ S- rep2'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['F1'], 'F1 E- S+ rep1'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['G1'], 'G1 E- S+ rep2'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['H1'], 'H1 E- S- rep1')
    ]

    substrateWells = [
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['A2'], 'A2 10uM Sub'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['B2'], 'B2 10uM Sub'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['C2'], 'C2 10uM Sub'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['D2'], 'D2 10% DMSO'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['E2'], 'E2 10% DMSO'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['F2'], 'F2 10uM Sub'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['G2'], 'G2 10uM Sub'),
        WDef(nuncP96_2mL, nuncP96_2mL.wells_by_name()['H2'], 'H2 10% DMSO')
    ]
    # ----------------  END OF RXN WELL SETUP   ----------------
    # ----------------  END OF LABWARE INIT.    ----------------
    # ----------------  PIPETTE INITIALIZATION  ----------------

    # Load Pipettes
    lPipette = protocol.load_instrument(
        'p300_single_gen2', 'left', [tipR_300_3])

    rPipette = protocol.load_instrument(
        'p300_multi_gen2', 'right', [tipR_300_1, tipR_300_2])

    # Alias pipette
    p300s = lPipette
    p300m = rPipette

    # Initialize flow rate (faster than default)
    lPipette.flow_rate.aspirate = 100
    lPipette.flow_rate.dispense = 100

    rPipette.flow_rate.aspirate = 100
    rPipette.flow_rate.dispense = 100

    # ----------------  END OF PIPETTE INIT.    ----------------
    # ----------------  END OF EQUIPMENT AND LABWARES   --------

    # ----------------  HELPER FUNCTIONS        ----------------

    # defaultTipDisc(p, destSpot)
    # discard the pipette tip on p to destination rack spot destSpot or Trash

    def defaultTipDisc(p, destSpot='trash'):
        # Parse default behavior definition
        if defaultTipDiscardDest == TO_RACK:
            # Return tip to destRack if matching TO_RACK
            p.return_tip(destSpot)

        elif defaultTipDiscardDest == TO_TRASH:
            # Discard tip to #12 (trash bin) if matching TO_TRASH
            p.drop_tip()
        else:
            # Bad definition (non-fatal)
            print('WARNING: Current protocol does not have a valid definition of "defaultTipDiscardDest":',
                  defaultTipDiscardDest, ', fallback by discarding tip in trash')
            # Fallback behavior would be drop to trash
            p.drop_tip()

    # defaultTipDisc(p, dest, destSpot)
    # discard the pipette tip on p according to a specified dest string, to destination rack spot destSpot, trash, or default behavior
    def tipDisc(p, dest: str, destSpot=None):
        # Parse behavior definition
        if dest == TO_RACK:
            p.drop_tip(destSpot)

        elif dest == TO_TRASH:
            p.drop_tip()

        elif dest == TO_DEF:
            # Explicit default call
            defaultTipDisc(p, destSpot)
        else:
            # Bad dest definition, use protocol default
            print('WARNING: Invalid definition of "dest":', dest,
                  ', fallback by using default discard method')
            defaultTipDisc(p, destSpot)

    # ----------------  END OF HELPER FUNCTIONS ----------------

    # ----------------  START OF PROGRAM        ----------------

    # Fill C3694 Well A1-H10 w/ 25uL ea. quenching buffer, blow out last 10uL back into tube
    p300s.pick_up_tip()
    for col in range(10):
        # Aspirate each column 1-10
        p300s.aspirate(210, qBuf, 0.5)
        for row in range(8):
            # Pipette each row of column A-H 25uL
            p300s.dispense(25, microP96_C3694.wells()[8*col + row])
        # Blow out rest in tip
        p300s.blow_out(qBuf)
    p300s.drop_tip()

    # Prepare 8x 30uL lysate/lysis buffer + 240uL rxn buffer reaction mix w/o substrate

    # Lysate first
    for row in range(8):
        # Pipette each row of column 1 A-H 30uL according to E+ or E- in well desc
        if 'E+' in rxnWells[row].desc:
            p300s.transfer(30, lysate, rxnWells[row].well)
        else:
            p300s.transfer(30, lysBuf, rxnWells[row].well)

    # Rxn buffer acidification of lysate
    # Pipette 240uL of reaction buffer in each well A1-H1
    p300s.transfer(30, rBuf, rxnWells[0].plate.columns_by_name()[
                   '1'], new_tip='once')

    # Pause before starting rxn
    protocol.pause(
        'Check if mixture and plate are ready. Resuming will start pipetting substrate.')

    # Add substrates
    p300m.pick_up_tip()
    p300m.transfer(30, substrateWells[0].well,
                   rxnWells[0].well, new_tip='never')
    p300m.mix(5, 150)
    p300m.drop_tip()
    # Timepoint 1-10
    delayTimes = [30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0]
    for tp in range(10):
        # delay first
        protocol.delay(delayTimes[tp])
        # transfer to C3694
        p300m.transfer(25, rxnWells[0].well,
                       microP96_C3694.columns()[tp][0], True)

    # Finalizing cleanup
    if p300m.has_tip:
        p300m.drop_tip()
    if p300s.has_tip:
        p300s.drop_tip()
    protocol.pause('Sequence complete.')
