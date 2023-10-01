#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Tobias Karger und Marie Berger
# Contact: coding@thepatchwork.de
# License: The Unlicense, see LICENSE file.

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

PYKEEPASS_IMP_ERR = None
try:
    from pykeepass import PyKeePass
    import pykeepass.exceptions
except ImportError:
    PYKEEPASS_IMP_ERR = traceback.format_exc()
    pykeepass_found = False
else:
    pykeepass_found = True

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['release'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: keepass_group
short_description: Manage groups in a KeePass (kdbx) database.
version_added: "1.0"
description:
    - "This module allows you to manage groups in a KeePass (kdbx) database."
requirements:
    - PyKeePass
options:
    database:
        description:
            - Path of the KeePass database.
        required: true
        type: str
    name:
        description:
            - Name of the group.
        required: true
        type: str
    keyfile:
        description:
            - Path of the KeePass keyfile. Either this or 'database_password' (or both) are required.
        required: false
        type: str
    database_password:
        description:
            - Database password. Either this or 'keyfile' (or both) are required.
        required: false
        type: str
    icon_id:
        description:
            - Icon ID to be associated with the group.
        required: false
        type: str
        default: 48
    action:
        description:
            - The action to perform (create, modify, delete).
        required: true
        choices: ['create', 'modify', 'delete']
        type: str
    notes:
        description:
            - Notes for the group.
        required: false
        type: str
    new_name:
        description:
            - The new name for the group (only for modifications).
        required: false
        type: str
author:
    - Tobias Karger und Marie Berger
'''

EXAMPLES = '''
- name: Create a new group in KeePass
  keepass_group:
    action: create
    database: /path/to/keepass.kdbx
    database_password: "your_database_password"
    name: MyNewGroup
    icon_id: 48
    notes: This is a new group created by Ansible.
  register: group

- debug:
    var: group

- name: Modify a groupname in KeePass
  keepass_group:
    action: modify
    database: /path/to/keepass.kdbx
    database_password: "your_database_password"
    name: MyNewGroup
    new_name: MyAwsomeNewGroup
  register: group

- debug:
    var: group

- name: Delete a group in KeePass
  keepass_group:
    action: delete
    database: /path/to/keepass.kdbx
    database_password: "your_database_password"
    name: MyAwsomeNewGroup
  register: group

- debug:
    var: group
'''

RETURN = '''
group:
    description: The name of the group created or modified.
    type: str
icon_id:
    description: The Icon ID associated with the group.
    type: str
notes:
    description: The notes associated with the group.
    type: str
changed:
    description: Indicates whether a change was made to the group.
    type: bool
'''

def main():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        database=dict(type='str', required=True),
        name=dict(type='str', required=True),
        keyfile=dict(type='str', required=False, default=None),
        database_password=dict(type='str', required=False, default=None, no_log=True),
        icon_id=dict(type='str', required=False),
        action=dict(type='str', required=True),
        notes=dict(type='str', required=False),
        new_name=dict(type='str', required=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        name=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not pykeepass_found:
        module.fail_json(msg=missing_required_lib("pykeepass"), exception=PYKEEPASS_IMP_ERR)

    database                = module.params['database']
    keyfile                 = module.params['keyfile']
    database_password       = module.params['database_password']
    name                    = module.params['name']
    icon_id                 = module.params['icon_id']
    action                  = module.params['action']
    notes                   = module.params['notes']
    new_name                = module.params['new_name']

    if (action.lower() == "create" and new_name) or (action.lower() == "delete" and new_name) :
        module.fail_json(msg="Action 'Create' or 'Delete' do not take 'new_name'")

    if not database_password and not keyfile:
        module.fail_json(msg="Either 'database_password' or 'keyfile' (or both) are required.")

    try:
        kp = PyKeePass(database, password=database_password, keyfile=keyfile)
    except IOError:
        KEEPASS_OPEN_ERR = traceback.format_exc()
        module.fail_json(msg='Could not open the database or keyfile.')
    except pykeepass.exceptions.CredentialsError:
        KEEPASS_OPEN_ERR = traceback.format_exc()
        module.fail_json(msg='Could not open the database, as the credentials are wrong.')
    except (pykeepass.exceptions.HeaderChecksumError, pykeepass.exceptions.PayloadChecksumError):
        KEEPASS_OPEN_ERR = traceback.format_exc()
        module.fail_json(msg='Could not open the database, as the checksum of the database is wrong. This could be caused by a corrupt database.')

    if action.lower() == "create":
        # try to get the entry from the database
        group = kp.find_groups(name=name, first=True)
        if group:
            if group.name == name:
                result['icon_id'] = group.icon
                result['name']    = group.name
                result['notes']   = group.notes
                module.exit_json(**result)

        if not module.check_mode:
            try:
                kp.add_group(kp.root_group, group_name=name, icon=icon_id or '48', notes=notes or 'Generated by ansible.')
                kp.save()
            except:
                KEEPASS_SAVE_ERR = traceback.format_exc()
                module.fail_json(msg='Could not add the group or save the database.', exception=KEEPASS_SAVE_ERR)

        group = kp.find_groups(name=name, first=True)

        result['name']     = group.name
        result['icon_id']   = group.icon
        result['notes']     = group.notes
        result['changed']   = True

        # in the event of a successful module execution, you will want to
        # simple AnsibleModule.exit_json(), passing the key/value results
        module.exit_json(**result)

    elif action.lower() == "modify":
        # try to get the entry from the database
        group = kp.find_groups(name=name)
        if len (group) > 1:
            module.fail_json(msg='More then one group found in Database', exception=traceback.format_exc())
        elif len (group) == 0:
            module.fail_json(msg='No group found in Database', exception=traceback.format_exc())
        else:
            group = group[0]
            if notes:
                group.notes = notes

            if icon_id:
                group.icon = icon_id

            if new_name:
                group.name = new_name

            kp.save()

            result['name']      = group.name
            result['icon_id']   = group.icon
            result['notes']     = group.notes
            result['changed']   = True

        # in the event of a successful module execution, you will want to
        # simple AnsibleModule.exit_json(), passing the key/value results
        module.exit_json(**result)

    elif action.lower() == "delete":
        group = kp.find_groups(name=name)
        if len (group) > 1:
            module.fail_json(msg='More then one entry found in Database', exception=traceback.format_exc())
        elif len (group) == 0:
            module.fail_json(msg='No entry found in Database', exception=traceback.format_exc())
        else:
            kp.delete_group(group=group[0])
            kp.save()
            module.exit_json(changed=True)

    else:
        module.fail_json(msg='No action matched', exception=traceback.format_exc())

def generate_password(length):
    import string
    alphabet = string.ascii_letters + string.digits
    try:
        import secrets as random
    except ImportError:
        import random

    gen_password = ''.join(random.choice(alphabet) for _ in range(length))
    return gen_password

if __name__ == '__main__':
    main()