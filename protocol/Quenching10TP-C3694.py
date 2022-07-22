from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from opentrons import protocol_api
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
    deckLabware = [
        LDef(1, 'corning_96_wellplate_halfarea_190ul_flat', True),
        LDef(2, '', False),
        LDef(3, '', False),
        LDef(4, 'opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', True),
        LDef(5, 'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', True),
        LDef(6, '', False),
        LDef(7, '', False),
        LDef(8, '', False),
        LDef(9, '', False),
        LDef(10, 'opentrons_96_tiprack_300ul', True),
        LDef(11, 'opentrons_96_tiprack_1000ul', True),
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
    tipR_300_1 = deckRefs[10]
    tipR_1000_1 = deckRefs[11]
    # tipR_20F
    # tipR_300F
    # tipR_1000F

    tubeR_24xEpp = deckRefs[5]
    tubeR_6x15_4x50 = deckRefs[4]
    # tubeR_15x15
    # tubeR_6x50

    # aluB_24w
    # aluB_96w
    # aluB_flat

    # CORNING:
    microP96_C3694 = deckRefs[1]

    # ----------------  END OF LABWARE INIT.    ----------------
    # ----------------  PIPETTE INITIALIZATION  ----------------

    # Specify tip rack arrays
    tipR_20_List = []
    tipR_300_List = [tipR_300_1]
    tipR_1000_List = [tipR_1000_1]
    tipR_20F_List = []
    tipR_300F_List = []
    tipR_1000F_List = []

    # Load Pipettes
    lPipette = protocol.load_instrument(
        'p1000_single_gen2', 'left', tipR_1000_List)

    rPipette = protocol.load_instrument(
        'p300_multi_gen2', 'right', tipR_300_List)

    # ----------------  END OF PIPETTE INIT.    ----------------
    # ----------------  END OF EQUIPMENT AND LABWARES   --------

    # ----------------  HELPER FUNCTIONS        ----------------

    # defaultTipDisc(p, destRack)
    # discard the pipette tip on p to destination destRack or Trash
    def defaultTipDisc(p, destRack):
        # Parse default behavior definition
        if defaultTipDiscardDest == TO_RACK:
            # Return tip to destRack if matching TO_RACK
            p.return_tip(destRack)

        elif defaultTipDiscardDest == TO_TRASH:
            # Discard tip to #12 (trash bin) if matching TO_TRASH
            p.drop_tip()
        else:
            # Bad definition (non-fatal)
            print('WARNING: Current protocol does not have a valid definition of "defaultTipDiscardDest":',
                  defaultTipDiscardDest, ', fallback by discarding tip in trash')
            # Fallback behavior would be drop to trash
            p.drop_tip()

    # defaultTipDisc(p, dest, destRack)
    # discard the pipette tip on p according to a specified dest string, to destination destRack, trash, or default behavior
    def tipDisc(p, dest: str, destRack):
        # Parse behavior definition
        if dest == TO_RACK:
            p.return_tip(destRack)

        elif dest == TO_TRASH:
            p.drop_tip()

        elif dest == TO_DEF:
            # Explicit default call
            defaultTipDisc(p, destRack)
        else:
            # Bad dest definition, use protocol default
            print('WARNING: Invalid definition of "dest":', dest,
                  ', fallback by using default discard method')
            defaultTipDisc(p, destRack)

    # ----------------  END OF HELPER FUNCTIONS ----------------

    # ----------------  START OF PROGRAM        ----------------
    # Add Diluent
    left_pipette.flow_rate.aspirate = 100
    left_pipette.flow_rate.dispense = 100

    left_pipette.pick_up_tip(m300rack['A1'])
    for j in range(plateCol//3):
        left_pipette.aspirate(300, trough.wells()[11].bottom(2))
        for i in range(3):
            left_pipette.dispense(90, plate_96.wells()[i*8+j*24].bottom(4))
        left_pipette.blow_out(trough.wells()[11])
    left_tips(discard_tips, m300rack['A1'])

    # Dilute lysate and transfer to 384-well plate
    right_pipette.flow_rate.aspirate = 40
    right_pipette.flow_rate.dispense = 40

    for i in range(plateCol):
        right_pipette.pick_up_tip(m20rack['A'+str(i+1)])
        right_pipette.transfer(10, plate_96_2.wells()[
                               i*8], plate_96.wells()[i*8], mix_after=(5, 20), new_tip='never')
        for j in range(4):
            if i//3 % 2 < 1:
                right_pipette.aspirate(20, plate_96.wells()[i*8])
                right_pipette.dispense(10, plate_384.wells()[
                                       i*16+j*96-i//3//2*48])
                right_pipette.blow_out(plate_96.wells()[i*8])
            else:
                right_pipette.aspirate(20, plate_96.wells()[i*8])
                right_pipette.dispense(10, plate_384.wells()[
                                       (i-3)*16+j*96+1-i//3//2*48])
                right_pipette.blow_out(plate_96.wells()[i*8])
        right_tips(discard_tips, m20rack['A'+str(i+1)])

    protocol.pause('Add substrates!')

    # Add substrates
    left_pipette.pick_up_tip(m300rack['A2'])
    left_pipette.mix(3, 300, trough.wells()[0].bottom(2))
    for i in range(int(plateCol/3)):
        left_pipette.aspirate(170, trough.wells()[0].bottom(2))
        for j in range(3):
            if i*3//3 % 2 < 1:
                left_pipette.dispense(50, plate_384.wells()[
                                      j*16+i*3//3//2*48].bottom(10))
            else:
                left_pipette.dispense(50, plate_384.wells()[
                                      j*16+1+i*3//3//2*48].bottom(10))
        left_pipette.blow_out(trough.wells()[0])
    left_tips(discard_tips, m300rack['A2'])

    left_pipette.pick_up_tip(m300rack['A3'])
    left_pipette.mix(3, 300, trough.wells()[1].bottom(2))
    for i in range(int(plateCol/3)):
        left_pipette.aspirate(170, trough.wells()[1].bottom(2))
        for j in range(3):
            if i*3//3 % 2 < 1:
                left_pipette.dispense(50, plate_384.wells()[
                                      j*16+i*3//3//2*48+96].bottom(10))
            else:
                left_pipette.dispense(50, plate_384.wells()[
                                      j*16+1+i*3//3//2*48+96].bottom(10))
        left_pipette.blow_out(trough.wells()[1])
    left_tips(discard_tips, m300rack['A3'])

    left_pipette.pick_up_tip(m300rack['A4'])
    left_pipette.mix(3, 300, trough.wells()[2].bottom(2))
    for i in range(int(plateCol/3)):
        left_pipette.aspirate(170, trough.wells()[2].bottom(2))
        for j in range(3):
            if i*3//3 % 2 < 1:
                left_pipette.dispense(50, plate_384.wells()[
                                      j*16+i*3//3//2*48+192].bottom(10))
            else:
                left_pipette.dispense(50, plate_384.wells()[
                                      j*16+1+i*3//3//2*48+192].bottom(10))
        left_pipette.blow_out(trough.wells()[2])
    left_tips(discard_tips, m300rack['A4'])

    left_pipette.pick_up_tip(m300rack['A5'])
    left_pipette.mix(3, 300, trough.wells()[3].bottom(2))
    for i in range(int(plateCol/3)):
        left_pipette.aspirate(170, trough.wells()[3].bottom(2))
        for j in range(3):
            if i*3//3 % 2 < 1:
                left_pipette.dispense(50, plate_384.wells()[
                                      j*16+i*3//3//2*48+288].bottom(10))
            else:
                left_pipette.dispense(50, plate_384.wells()[
                                      j*16+1+i*3//3//2*48+288].bottom(10))
        left_pipette.blow_out(trough.wells()[3])
    left_tips(discard_tips, m300rack['A5'])
