from opentrons import protocol_api
# metadata
metadata = {
    'protocolName': '10-timepoint Quenching Assay',
    'author': 'Lux <lux011@brandeis.edu>',
    'description': 'Prototype protocol to prepare, start, taketimepoints and quench into a Corning 3694 96 well fluorescence microplate. Adapted from JYChow@NUS',
    'apiLevel': '2.12'}


def run(protocol: protocol_api.ProtocolContext):

    plateCol = 12  # Number of columns in 96-well plate, in triplicates of 3, 6, 9 or 12
    # Enter 'yes' to discard tips into trash, 'no' for tips to return to the pipette tip boxes
    discard_tips = 'no'

    def left_tips(tip, rack):
        if tip == 'yes':
            left_pipette.drop_tip()
        if tip == 'no':
            left_pipette.return_tip(rack)

    def right_tips(tip, rack):
        if tip == 'yes':
            right_pipette.drop_tip()
        if tip == 'no':
            right_pipette.return_tip(rack)

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
