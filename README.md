# Ansible Collection - torie_coding.keepass

These Ansible modules allow you to manage entries and groups in a KeePass (kdbx) database.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Modules](#modules)
  - [entry](#entry)
  - [group](#group)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Prerequisites

Before using these Ansible modules, you need to ensure the following prerequisites are met:

- Ansible installed on your system.
- Python module "pykeepass" installed. You can install it using `pip install pykeepass`.

## Modules

### entry

This Ansible module allows you to manage entries in a KeePass (kdbx) database.

#### Paramters

- `database` (required): Path to the KeePass database.
- `title` (required): Title of the entry you want to manage.
- `username` (required): Username of the entry.
- `action` (required): The action to perform (create, modify, delete).
- `keyfile`: Path to the KeePass key file. Either this or 'database_password' (or both) are required.
- `database_password`: Database password. Either this or 'keyfile' (or both) are required.
- `password_length`: The length of the password that should be generated (only needed if no password is provided). Default length for action 'create' is 20.
- `password`: The password that will be set for the entry (if on action 'create' no password is given, a password will be generated with given 'password_length').
- `url`: URL that will be set for the KeePass entry.
- `group_name`: Group name in which the KeePass entry is placed.
- `icon_id`: Icon ID to be associated with the KeePass entry.



#### Example

```yaml
- name: Create a new entry in KeePass
  keepass_entry:
    action: create
    database: /path/to/keepass.kdbx
    database_password: "your_database_password"
    title: MyNewEntry
    username: myusername
    password: mypassword
    url: https://example.com
    group_name: MyGroup
    icon_id: 49
  register: entry

- name: Create a new entry in KeePass with generated password
  keepass_entry:
    action: create
    database: /path/to/keepass.kdbx
    database_password: "your_database_password"
    title: MyNewEntry
    username: myusername
    password_length: 16
    url: https://example.com
    group_name: MyGroup
    icon_id: 49
  register: entry

- name: Modify the URL of an entry in KeePass
  keepass_entry:
    action: modify
    database: /path/to/keepass.kdbx
    database_password: "your_database_password"
    title: MyNewEntry
    url: https://example.com
  register: entry

- debug:
    var: entry

- name: Delete an entry in KeePass
  keepass_entry:
    action: delete
    database: /path/to/keepass.kdbx
    database_password: "your_database_password"
    title: MyNewEntry
  register: entry

- debug:
    var: entry
```
### group

This Ansible module allows you to manage groups in a KeePass (kdbx) database.

#### Paramters

- `database` (required): Path to the KeePass database.
- `name` (required): Name of the group you want to manage.
- `action` (required): The action to perform (create, modify, delete).
- `keyfile`: Path of the KeePass key file. Either this or 'database_password' (or both) are required.
- `database_password`: Database password. Either this or 'keyfile' (or both) are required.
- `icon_id`: Icon ID to be associated with the group. Defaults to '48'.
- `notes`: Notes for the group.
- `new_name`: The new name for the group (only for modifications).

#### Example

```yaml
- name: Create a new group in KeePass
  keepass_group:
    action: create
    database: /path/to/keepass.kdbx
    database_password: "your_database_password"
    name: MyNewGroup
    icon_id: 49
    notes: This is a new group created by Ansible.
  register: group

- debug:
    var: group

- name: Modify a group name in KeePass
  keepass_group:
    action: modify
    database: /path/to/keepass.kdbx
    database_password: "your_database_password"
    name: MyNewGroup
    new_name: MyAwesomeNewGroup
  register: group

- debug:
    var: group

- name: Delete a group in KeePass
  keepass_group:
    action: delete
    database: /path/to/keepass.kdbx
    database_password: "your_database_password"
    name: MyAwesomeNewGroup
  register: group

- debug:
    var: group

```
## Installation

Before you can use this module, make sure you have Ansible and pykeepass installed on your system. Additionally, you need to install the "torie_coding.keepass" Ansible collection. You can do this using Ansible Galaxy, which is Ansible's official hub for sharing Ansible content.

To install the "torie_coding.keepass" collection, run the following command:

```shell
ansible-galaxy collection install torie_coding.keepass
```

## License

This Ansible collection is open-source and available under The Unlicense, a permissive open-source license. You can find the full text of the license in the [LICENSE](LICENSE) file included in this repository.

You are free to use, modify, and distribute this collection as you see fit. There are no restrictions or obligations imposed by the license, so feel free to adapt it to your needs.

We encourage contributions to this collection from the community. If you find issues, have ideas for improvements, or want to add new features, please consider contributing to make this collection even better.

For any questions or concerns related to the license or usage of this collection, please contact us at [coding@thepatchwork.de](mailto:coding@thepatchwork.de).
