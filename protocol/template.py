from multiprocessing.sharedctypes import Value
from opentrons import protocol_api
# metadata
metadata = {
    'protocolName': 'Template',
    'author': 'Lux <lux011@brandeis.edu>',
    'description': 'template to use with Opentrons OT-2, including various functions and loop blocks',
    'apiLevel': '2.12'}

# GLOBAL VARIABLE DEFINITION
TO_TRASH = 'trash'
TO_RACK = 'rack'
TO_DEF = 'default'


def run(protocol: protocol_api.ProtocolContext):

    # ----------------  RUN VARAIBLES   ------------------------
    plateCol = 12  # Number of columns in 96-well plate, in triplicates of 3, 6, 9 or 12

    defaultTipDiscardDest = TO_TRASH    # Default to discard used tips into tray 12 trash bin
    #defaultTipDiscardDest = TO_RACK    # Default to return used tips back into specified rack


    # ----------------  END OF RUN VARAIBLES    ----------------
    # ----------------  EQUIPMENT AND LABWARES  ----------------

    # LABWARES
    m300rack = protocol.load_labware('opentrons_96_tiprack_300ul', '1')
    m20rack = protocol.load_labware('opentrons_96_tiprack_20ul', '4')
    plate_96 = protocol.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul', '2')
    plate_96_2 = protocol.load_labware(
        'opentrons_96_aluminumblock_generic_pcr_strip_200ul', '5')
    plate_384 = protocol.load_labware('corning_384_wellplate_112ul_flat', '3')
    trough = protocol.load_labware('usascientific_12_reservoir_22ml', '6')

    left_pipette = protocol.load_instrument('p300_multi', 'left',
                                            tip_racks=[m300rack])
    right_pipette = protocol.load_instrument(
        'p20_multi_gen2', 'right', tip_racks=[m20rack])
    # ----------------  END OF EQUIPMENT AND LABWARES   --------
    # ----------------  HELPER FUNCTIONS    --------------------

    # Pipette Tip Default Discarding Destination: Helper Function
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

    # Pipette Tip Discarding Destination Helper Function
    # defaultTipDisc(p, dest, destRack)
    # discard the pipette tip on p according to a specified dest string, to destination destRack, trash, or default behavior
    def tipDisc(p, dest, destRack):
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
