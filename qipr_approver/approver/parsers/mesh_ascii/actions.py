from datetime import date

from django.contrib.auth.models import User

from approver.models import *
import approver.utils as utils
from approver.constants import total_qualifiers_2017

fixture_user = User.objects.get(id=1)

qualifier_count = len(Qualifier.objects.all())

actions = {
    'save': lambda acc, RHS: acc.save(fixture_user),
    '*NEWRECORD': lambda acc, RHS: acc,
    'AN': lambda acc, RHS: set_return(acc, 'annotation', RHS),
    'AQ': lambda acc, RHS: set_qualifiers(acc, RHS),
    'CATSH': lambda acc, RHS: acc,
    'DA': lambda acc, RHS: set_date(acc, 'date_added', RHS),
    'DC': lambda acc, RHS: set_return(acc, 'descriptor_class', RHS),
    'DE': lambda acc, RHS: set_return(acc, 'descriptor_entry_version', RHS),
    'DQ': lambda acc, RHS: set_date(acc, 'qualifier_established', RHS),
    'DS': lambda acc, RHS: set_return(acc, 'descriptor_sort_version', RHS),
    'DX': lambda acc, RHS: set_date(acc, 'major_descriptor_date', RHS),
    'ENTRY': lambda acc, RHS: add_return(acc, 'entry', RHS, entry_lookup),
    'FR': lambda acc, RHS: set_return(acc, 'frequency', RHS),
    'HN': lambda acc, RHS: set_return(acc, 'history_note', RHS),
    'MH': lambda acc, RHS: set_return(acc, 'mesh_heading', RHS),
    'MN': lambda acc, RHS: set_return(acc, 'mesh_tree_number', RHS, mesh_num_lookup),
    'MR': lambda acc, RHS: set_date(acc, 'major_revision_date', RHS),
    'MS': lambda acc, RHS: set_return(acc, 'mesh_scope_note', RHS),
    'NM': lambda acc, RHS: set_return(acc, 'substance_name', RHS),
    'NM_TH': lambda acc, RHS: set_return(acc, 'substance_name_term_thesaurus', RHS),
    'NO': lambda acc, RHS: set_return(acc, 'note', RHS),
    'PA': lambda acc, RHS: add_return(acc, 'pharmacological_action', RHS, pharma_name_lookup),
    # this needs to be parsed out. complex data right now. Dont understand it
    'PRINT ENTRY': lambda acc, RHS: add_return(acc, 'entry', RHS, entry_lookup),
    'QA': lambda acc, RHS: set_return(acc, 'abbreviation', RHS),
    'RECTYPE': lambda acc, RHS: instantiate_mesh_model(acc, RHS),
    'RN': lambda acc, RHS: set_return(acc, 'cas_registry_number', RHS),
    'RR': lambda acc, RHS: add_return(acc, 'related_registry_number', RHS, reg_num_lookup),
    'SH': lambda acc, RHS: set_return(acc, 'sub_heading', RHS),
    'SO': lambda acc, RHS: add_return(acc, 'source', RHS, source_lookup),
    'ST': lambda acc, RHS: add_return(acc, 'semantic_type', RHS, semantic_lookup),
    'SY': lambda acc, RHS: add_return(acc, 'synonym', RHS, synonym_lookup),
    'UI': lambda acc, RHS: set_return(acc, 'ui', RHS),
}

def instantiate_mesh_model(acc, RHS):
    model_funcs = {
        'D': Descriptor,
        'Q': Qualifier,
        'C': SCR,
    }
    model = model_funcs[RHS]()
    model.save(fixture_user)
    return model

def set_return(model, prop, value, mapping=lambda x:x):
    setattr(model, prop, mapping(value))
    return model

def parse_date(yyyymmdd):
    year = int(yyyymmdd[0:4])
    month = int(yyyymmdd[4:6])
    day = int(yyyymmdd[6:8])
    return date(year=year, month=month, day=day)

def set_date(model, prop, value):
    my_date = parse_date(value)
    return set_return(model, prop, my_date)

def set_qualifiers(model, quals):
    quals = quals.split(' ')
    for qual in quals:
        if len(qual) == 2:
            if qualifier_count == total_qualifiers_2017:
                qualifier = Qualifier.objects.get(abbreviation=qual)
            else:
                qualifier = utils.get_or_instantiate(Qualifier, {'abbreviation': qual})
                qualifier.save(fixture_user)
            model.allowable_qualifiers.add(qualifier)
    return model

def set_consider_also(model, RHS):
    # there arent very many of these but we will want to break them into something
    # nicer than just the nasty string that they are now
    model.consider_also = RHS
    return model

def add_return(model, prop, RHS, mapping=lambda x:x):
    manager = getattr(model, prop)
    manager.add(mapping(RHS))
    return model

def desc_mh_lookup(string):
    models = Descriptor.objects.filter(mesh_heading__startswith=string)
    return models[0]

def pharma_name_lookup(string):
    model = utils.get_or_instantiate(PharmacologicalAction, {'name':string})
    model.save(fixture_user)
    return model

def entry_lookup(string):
    model = utils.get_or_instantiate(Entry, {'pipe_separated':string})
    model.name = string.split('|')[0]
    model.save(fixture_user)
    return model

def reg_num_lookup(string):
    model = utils.get_or_instantiate(RegistryNumber, {'name':string})
    model.save(fixture_user)
    return model

def source_lookup(string):
    model = utils.get_or_instantiate(Source, {'name':string})
    model.save(fixture_user)
    return model

def semantic_lookup(string):
    model = utils.get_or_instantiate(SemanticType, {'value':string})
    model.save(fixture_user)
    return model

def synonym_lookup(string):
    model = utils.get_or_instantiate(Synonym, {'pipe_separated':string})
    model.name = string.split('|')[0]
    model.save(fixture_user)
    return model

def mesh_num_lookup(string):
    model = MeshTreeNumber(value=string)
    model.save(fixture_user)
    return model
