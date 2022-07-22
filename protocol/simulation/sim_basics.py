from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'My basic protocol',
    'description': 'Some random test protocol',
    'apiLevel': '2.12'
}

def run(protocol: protocol_api.ProtocolContext):
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 1)
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', 2)
    p300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tiprack_1])

    p300.pick_up_tip()
    p300.aspirate(100, plate['A1'])
    p300.dispense(100, plate['B1'])
    p300.drop_tip()