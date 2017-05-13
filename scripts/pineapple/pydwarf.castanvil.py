import pydwarf



default_entities = 'MOUNTAIN'

default_anvil_cost = 5 # Cost in iron bars

default_file = 'raw/objects/reaction_smelter_castanvil_pineapple.txt'



@pydwarf.urist(
    name = 'pineapple.castanvil',
    title = 'Cast Anvil at Smelter',
    version = '1.0.1',
    author = 'Sophie Kirschner',
    description = '''Adds a reaction to the smelter which makes it possible to
        create an iron anvil without already having a forge.
        Inspired by/stolen from Rubble's Cast Anvil mod.''',
    arguments = {
        'anvil_cost': 'The cost in iron bars to create an anvil in this way. Defaults to 5.',
        'entities': 'Adds the reaction to these entities. Defaults to only MOUNTAIN.',
        'add_to_file': 'Adds the reaction to this file.'
    },
    compatibility = (pydwarf.df_0_3x, pydwarf.df_0_40)
)
def castanvil(df, anvil_cost=default_anvil_cost, entities=default_entities, add_to_file=default_file):
    # Super easy using pineapple.utils
    return pydwarf.urist.getfn('pineapple.utils.addobject')(
        df,
        type = 'REACTION',
        id = 'CAST_IRON_ANVIL_PINEAPPLE',
        tokens = '''
            [NAME:cast iron anvil]
            [BUILDING:SMELTER:NONE]
            [REAGENT:A:%d:BAR:NO_SUBTYPE:METAL:IRON]
            [PRODUCT:100:1:ANVIL:NONE:METAL:IRON]
            [FUEL]
            [SKILL:SMELT]
        ''' % (anvil_cost * 150),
        add_to_file = add_to_file,
        permit_entities = entities
    )
