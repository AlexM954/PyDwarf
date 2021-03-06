import pydwarf
import raws



@pydwarf.urist(
    name = 'pineapple.utils.addtoentity',
    version = '1.0.3',
    author = 'Sophie Kirschner',
    description = '''A simple utility script which adds tokens to entities.''',
    arguments = {
        'entities': 'Adds tokens to these entities. If this is the string "*" then tokens are added to all entities.',
        'tokens': 'A string or collection of tokens to add to each entity.',
    },
    compatibility = '.*'
)
def addtoentity(df, entities, tokens):
    if entities == '*':
        pydwarf.log.debug('Adding tokens to all entities.')
        entitytokens = df.allobj(type='ENTITY')
    else:
        if isinstance(entities, basestring):
            entities = (entities,)
        pydwarf.log.debug('Adding tokens to entities %s.' % ', '.join(str(ent) for ent in entities))
        entitytokens = df.allobj(type='ENTITY', id_in=entities)
    
    for entitytoken in entitytokens:
        entitytoken.addprop(tokens)
        if isinstance(tokens, raws.queryable): tokens = raws.helpers.copy(tokens) # TODO: What about other iterables containing token objects, e.g. lists and tuples?
        
    if entities != '*' and len(entitytokens) != len(entities):
        return pydwarf.failure('Failed to add tokens to all given entities because only %d of %d exist.' % (len(entitytokens), len(entities)))
    else:
        return pydwarf.success('Added tokens to %d entities.' % len(entitytokens))



@pydwarf.urist(
    name = 'pineapple.utils.objecttokens',
    version = '1.0.0',
    author = 'Sophie Kirschner',
    description = '''Utility script for adding or removing tokens from
        objects.''',
    arguments = {
        'object_type': '''The type of object which should be affected.''',
        'token': '''The token to be added or removed.''',
        'remove_from': '''If set to None, no matching tokens are removed. If
            set to '*', all matching tokens are removed. If set to an
            iterable containing IDs of objects, matching tokens will be
            removed from each of those objects.''',
        'add_to': '''If set to None, no tokens tokens are added. If set to
            '*', tokens are added to all objects. If set to an iterable
            containing IDs of objects, tokens will be added to each of
            those objects.'''
    },
    compatibility = '.*'
)
def objecttokens(df, object_type, token, add_to=None, remove_from=None):
    added, removed = 0, 0
    
    # Remove tokens
    if remove_from:
        for objtoken in df.allobj(type=object_type, id_in=(None if remove_from == '*' else remove_from)):
            for removetoken in objtoken.allprop(token): 
                removetoken.remove()
                removed += 1
        
    # Add tokens
    if add_to:
        for objtoken in df.allobj(type=object_type, id_in=(None if add_to == '*' else add_to)):
            if not objtoken.getprop(token):
                objtoken.addprop(token)
                added += 1
        
    # All done!
    if removed or added:
        return pydwarf.success('Added %d %s tokens and removed %d from object type %s.' % (added, token, removed, object_type))
    else:
        return pydwarf.failure('Didn\'t add or remove any %s tokens.' % token)  



@pydwarf.urist(
    name = 'pineapple.utils.addhack',
    version = '1.0.1',
    author = 'Sophie Kirschner',
    description = '''Utility script for adding a new DFHack script.''',
    arguments = {
        'auto_run': '''If set to True, a line will be added to dfhack.init containing only
            the name of the added script. If set to None, no such line will be added. If set
            to an arbitrary string, that string will be added as a new line at the end of
            dfhack.init.''',
        'onload': 'If set to True then the auto_run line will be added to raw/onLoad.init.',
        'startup': 'If set to True then the auto_run line will be added to dfhack.init.',
        '**kwargs': '''Other named arguments will be passed on to the dir.add method used to
            create the file object corresponding to the added script.'''
    },
    compatibility = '.*'
)
def addhack(df, auto_run, onload=True, startup=False, **kwargs):
    name = kwargs.get('name', kwargs.get('path', 'unnamed'))
    
    onload_path = 'raw/onLoad.init'
    startup_path = 'dfhack.init'
    
    if kwargs: 
        pydwarf.log.debug('Adding new file %s.' % name)
        hackfile = df.add(**kwargs)
    else:
        hackfile = None
    
    if auto_run:
        if auto_run is True:
            if not hackfile: return pydwarf.failure('Failed to add lines to DFHack because auto_run was True but no file was created.')
            auto_run = '\n%s' % hackfile.name
        
        pydwarf.log.debug('Adding text %s to the end of dfhack.init.' % auto_run)
        addtext = '\n%s\n' % auto_run
        
        if onload:
            if onload_path not in df:
                init = df.add(
                    loc = 'raw',
                    name = 'onLoad',
                    ext = '.init',
                    kind = raws.binfile
                )
            else:
                init = df[onload_path]
            init.add(addtext)
            
        if startup:
            if startup_path not in df:
                if 'dfhack.init-example' in df:
                    pydwarf.log.info('Copying dfhack.init-example to new file dfhack.init before adding new content to the file.')
                    init = df['dfhack.init-example'].copy().bin()
                    init.name = startup_path
                    df.add(file=init)
                else:
                    return pydwarf.failure('Failed to locate dfhack.init or dfhack.init-example.')
            else:
                init = df[startup_path].bin()
            init.add(addtext)
        
        return pydwarf.success(
            'Added text to %s: "%s"' % (
                ' and '.join(
                    item for item in (
                        onload_path if onload else None, startup_path if startup else None
                    ) if item
                ),
                auto_run
            )
        )
        
    else:
        return pydwarf.success('Added new file %s.' % name)



@pydwarf.urist(
    name = 'pineapple.utils.addobject',
    version = '1.0.1',
    author = 'Sophie Kirschner',
    description = '''Utility script for adding a new object to the raws.''',
    arguments = {
        'add_to_file': '''The name of the file to add the object to. If it doesn't exist already
            then the file is created anew. The string is formatted such that %(type)s is
            replaced with the object_header, lower case.''',
        'tokens': '''The tokens belonging to the object to create.''',
        'type': '''Specifies the object type. If type and id are left unspecified, the first
            token of the tokens argument is assumed to be the object's [TYPE:ID] token and the
            type and id arguments are taken out of that.''',
        'id': '''Specifies the object id. If type and id are left unspecified, the first
            token of the tokens argument is assumed to be the object's [TYPE:ID] token and the
            type and id arguments are taken out of that.''',
        'permit_entities': '''For relevant object types such as reactions, buildings, and items,
            if permit_entities is specified then tokens are added to those entities to permit
            the added object.''',
        'item_rarity': '''Most items, when adding tokens to entities to permit them, accept an
            optional second argument specifying rarity. It should be one of 'RARE', 'UNCOMMON',
            'COMMON', or 'FORCED'. This argument can be used to set that rarity.''',
        'object_header': '''When the object is added to a file which doesn't already exist,
            an [OBJECT:TYPE] token must be added at its beginning. This argument, if specified,
            provides the type in that token. Otherwise, when the argument is left set to None,
            the type will be automatically decided.'''
    },
    compatibility = '.*'
)
def addobject(df, add_to_file, tokens, type=None, id=None, permit_entities=None, item_rarity=None, object_header=None):
    # If type and id weren't explicitly given then assume the first given token is the TYPE:ID header and get the info from there.
    header_in_tokens = type is None and id is None
    header = None
    if header_in_tokens:
        if isinstance(tokens, basestring): tokens = raws.parseplural(tokens)
        header = tokens[0]
        type = header.value
        id = header.arg()
        pydwarf.log.debug('Extracted object type %s and id %s from given tokens.' % (type, id))
        
    # Get the applicable object dict which knows how to map TYPE:ID to its corresponding OBJECT:TYPE header.
    if object_header is None:
        object_header = raws.objects.headerforobject(type)
    
    # If add_to_file already exists, fetch it. Otherwise add it to the raws.
    add_to_file = add_to_file % {'type': object_header.lower()}
    if add_to_file in df:
        file = df.getfile(add_to_file)
    else:
        file = df.add(add_to_file)
        file.add(raws.token(value='OBJECT', args=[object_header]))
        pydwarf.log.debug('Added new file %s to dir.' % add_to_file)
    
    # Add the object itself to the raws.
    if not header_in_tokens: header = file.add(raws.token(value=type, args=[id]))
    file.add(tokens)
    
    # Add tokens to entities to permit the use of this object.
    if permit_entities:
        response = permitobject(
            df,
            type = type,
            id = id,
            permit_entities = permit_entities,
            item_rarity = item_rarity
        )
        if not response: return response
            
    # All done!
    return pydwarf.success('Added object %s to file %s.' % (header, file))



@pydwarf.urist(
    name = 'pineapple.utils.addobjects',
    version = '1.0.0',
    author = 'Sophie Kirschner',
    description = '''Utility script for adding several new objects to the raws at once.''',
    arguments = {
        'add_to_file': '''The name of the file to add the object to. If it doesn't exist already
            then the file is created anew. The string is formatted such that %(type)s is
            replaced with the object_header, lower case.''',
        'objects': '''An iterable containing tokens belonging to the objects to add.''',
        '**kwargs': 'Passed on to pineapple.utils.addobject.',
    },
    compatibility = '.*'
)
def addobjects(df, add_to_file, objects, **kwargs):
    for obj in objects:
        response = addobject(df, add_to_file, **kwargs)
        if not response.success: return response
    return response.success('Added %d objects.' % len(objects))



@pydwarf.urist(
    name = 'pineapple.utils.permitobject',
    version = '1.0.1',
    author = 'Sophie Kirschner',
    description = '''Utility script for permitting an object with entities.''',
    arguments = {
        'type': '''Specifies the object type.''',
        'id': '''Specifies the object id.''',
        'permit_entities': '''For relevant object types such as reactions,
            buildings, and items, if permit_entities is specified then tokens
            are added to those entities to permit the added object.
            If this is the string "*", then all entities will be permitted.''',
        'item_rarity': '''Some items, when adding tokens to entities to permit them, accept an
            optional second argument specifying rarity. It should be one of 'RARE', 'UNCOMMON',
            'COMMON', or 'FORCED'. This argument can be used to set that rarity.'''
    },
    compatibility = '.*'
)
def permitobject(df, type=None, id=None, permit_entities=None, all_entities=False, item_rarity=None):
    # Decide what tokens need to be added to the entities based on the object type
    if type == 'REACTION':
        tokens = raws.token(value='PERMITTED_REACTION', args=[id])
    elif type.startswith('BUILDING_'):
        tokens = raws.token(value='PERMITTED_BUILDING', args=[id])
    elif type.startswith('ITEM_'):
        value = type.split('_')[1]
        args = [id, item_rarity] if item_rarity else [id]
        tokens = raws.token(value=value, args=args)
    else:
        tokens = None
    
    pydwarf.log.debug('Permitting object [%s:%s] for %s entities.' % (
        type, id, 'all' if all_entities == '*' else len(permit_entities)
    ))
    
    # Actually add those tokens
    if tokens is None:
        return pydwarf.success('Didn\'t actually permit object [%s:%s] because objects of this type cannot be permitted.' % (type, id))
    elif not permit_entities:
        return pydwarf.failure('No entities were given for permitting.')
    else:
        response = addtoentity(
            df,
            entities = permit_entities,
            tokens = tokens
        )
        if not response:
            return response
        else:
            return pydwarf.success('Permitted object [%s:%s] for %d entities.' % (type, id, len(permit_entities)))
    
    
    
@pydwarf.urist(
    name = 'pineapple.utils.permitobjects',
    version = '1.0.0',
    author = 'Sophie Kirschner',
    description = '''Utility script for permitting several objects at once with entities.''',
    arguments = {
        'objects': '''An iterable containing either tokens or type, id tuples representing objects
            to be permitted.''',
        '**kwargs': 'Passed on to pineapple.utils.permitobject.',
    },
    compatibility = '.*'
)
def permitobjects(df, objects, **kwargs):
    pydwarf.log.debug('Permitting %d objects.' % len(objects))
    for item in objects:
        if isinstance(item, raws.token):
            type, id = item.value, item.arg()
        elif isinstance(item, basestring):
            type, id = item.split(':')
        else:
            type, id = item
        response = permitobject(df, type, id, **kwargs)
        if not response: return response
    return pydwarf.success('Permitted %d objects.' % len(objects))
    