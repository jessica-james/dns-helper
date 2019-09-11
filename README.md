To Do:
    Write playbook of use

To use:
    - Sample docker-compose included
    - Must be in the same Crate environment as a DNSMGMT service, Rancher services cannot communicate across environments to other services
    - It's possible to use an IP for the DNSMGMT endpoint, but DNSMGMT service must have port 9000 exposed.

    - Actions can only be 'create', 'update', 'delete' or 'validate'