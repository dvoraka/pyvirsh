#! /usr/bin/env python
# -*- coding: utf8 -*-
#

'''Module for libvirt shell.'''

import libvirt
import sys
import readline
import os
import atexit


class PyVirsh:
    '''Class for libvirt shell.'''

    def __init__(self):

        self.conn = None

        self.history_path = os.path.expanduser("~/.pyvirsh.history")
        atexit.register(self.save_shell_history)

        self.update_connect_completion()

        self.commands = [
            'list',
            'shutdown',
            'start',
            'quit'
        ]

        # shell completion logic
        self.logic = {
            'connect': {},
            'exit': {},
            'export': {},
            'import': {},
            'list': {},
            'resume': {},
            'shutdown': {},
            'start': {},
            'suspend': {},
            'test': {},
            'quit': {}
        }

    def update_domains_completion(self):
        '''Update domain names in shell completion.'''

        if self.conn is not None:

            domains = self.list_all_domains(self.conn)

            doms = {}

            for dom in domains:
                doms[dom[1]] = None

            self.logic['start'] = doms
            self.logic['shutdown'] = doms
            
            self.logic['suspend'] = doms
            self.logic['resume'] = doms

        return

    def update_connect_completion(self):
        '''Update connect strings.'''

        pass

    def connect(self, conn_str):
        '''Connect to server.'''

        self.conn = libvirt.open(conn_str)
        self.update_domains_completion()

        return

    def save_shell_history(self):
        '''Save shell history to file.'''

        readline.write_history_file(self.history_path)

        return

    def load_shell_history(self):
        '''Load history from file.'''

        if os.path.exists(self.history_path):
                readline.read_history_file(self.history_path)

        return

    def save_connect_history(self):
        '''Save connect history to file.'''

        pass

    def load_connect_history(self):
        '''Load connect history from file.'''

        pass

    def export_domain(self, domain):
        '''Export domain to archive.'''

        #xml = self.domain_xml_desc(domain, "FLAGS")

        pass

    def import_domain(self):
        '''Import domain from archive.'''

        #conn.defineXML(XML)

        pass

    def domain_xml_desc(self, domain, flags):
        '''Return domain XML description'''

        pass

    def run_shell(self):
        '''Run shell.'''

        run = 1

        self.load_shell_history()

        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.shell_completer2)
        readline.set_completer_delims(
            ' \t\n`~!@#$%^&*()=+[{]}\\|;:\'",<>/?')

        while run:
            try:

                comm = raw_input("# ")
            
            except EOFError:

                print('')
                sys.exit(0)

            self.simple_parse(comm)

            if comm == 'quit':

                run = 0

        return

    def list_all_domains(self, conn):
        '''Find all available domains and return list.'''

        domains = []

        for dom_id in conn.listDomainsID():

            dom = conn.lookupByID(dom_id)
            domains.append((str(dom_id), dom.name(), dom.isActive()))

        for dom in conn.listDefinedDomains():

            domain = conn.lookupByName(dom)
            domains.append(('-', dom, domain.isActive()))

        return domains

    @staticmethod
    def print_dom_info(values):
        '''Print domains info.'''

        print('{0:5} {1:20} {2:8}'.format("ID", "Name", "State"))
        print('-' * 40)
        for line in values:

            # TODO: more states
            state = ''
            if(line[2] == 0):
                state = 'shut off'
            else:
                state = 'running'

            print('{0:5} {1:20} {2:8}'.format(line[0], line[1], state))
            
        return

    @staticmethod
    def print_comm_not_found(command):
        '''Print info about bad command.'''

        print('{}: command not found'.format(command))

        return

    def find_domain(self, string):
        '''Find domain object from string and return it.'''

        for dom_id in self.conn.listDomainsID():

            domain = self.conn.lookupByID(dom_id)

            if string == domain.name():

                return domain

            try:
                if dom_id == int(string):

                    return domain

            except ValueError as error:

                print(error)
            
        for dom in self.conn.listDefinedDomains():
            try:
                if dom == string:

                    domain = self.conn.lookupByName(dom)

                    return domain

            except ValueError as error:

                print(error)

        return

    def resolve_domain(self, string):
        '''Resolve domain from string parameter and return domain object.'''

        domain = None
        choices = ('ID', 'name', 'UUID')
        for choice in choices:
            try:

                if (choice == 'ID'):

                    domain = self.conn.lookupByID(int(string))
                    break

                elif (choice == 'name'):

                    domain = self.conn.lookupByName(string)
                    break

                elif(choice == 'UUID'):

                    domain = self.conn.lookupByUUID(string)
                    break

            except libvirt.libvirtError:
#                print('libvirt error')
                pass

            except ValueError:
#                print('Value error')
                pass

            except TypeError:
#                print('Type error')
                pass

        return domain

    def simple_parse(self, data):
        '''Simple parser for commands.'''

        if(len(data) == 0):

            return

        commands = data.split()
        if (commands[0] == 'list'):

            self.print_dom_info(self.list_all_domains(self.conn))

        elif (commands[0] == 'export'):
            if (len(commands) == 2):

                self.export_domain(self.find_domain(commands[1]))

        elif (commands[0] == 'import'):
            if (len(commands) == 2):

                self.import_domain(commands[1])

        elif (commands[0] == 'resume'):
            if (len(commands) == 2):

                self.resume_domain(self.find_domain(commands[1]))

        elif (commands[0] == 'start'):
            if (len(commands) == 2):

                self.start_domain(commands[1])

        elif (commands[0] == 'shutdown'):
            if (len(commands) == 2):

                self.shutdown_domain(commands[1])

        elif (commands[0] == 'suspend'):
            if (len(commands) == 2):

                self.suspend_domain(self.find_domain(commands[1]))

        elif (commands[0] == 'quit' or commands[0] == 'exit'):

            sys.exit(0)

        # testing place
        elif(commands[0] == 'test'):

#            print(self.resolve_domain(commands[1]))
#            print(self.find_domain(commands[1]))
            self.suspend_domain(self.find_domain(commands[1]))

        else:

            self.print_comm_not_found(commands[0])

        return

    def shell_completer2(self, text, state):
        '''More complex method for shell completion.'''
        try:
            tokens = readline.get_line_buffer().split()
            
            if not tokens or readline.get_line_buffer()[-1] == ' ':

                tokens.append('')

            result = self.traverse(tokens, self.logic) + [None]

            return result[state]

        except IOError, error:
            print(error)

    def shell_completer(self, text, state):
        '''Method for shell completion.'''

        string = [choice for choice in self.commands
            if choice.startswith(text)]

        if state < len(string):

            return string[state]

        else:
            
            return None

    def shutdown_domain(self, name):
        '''Shutdown domain.'''

        domain = self.conn.lookupByName(name)
        domain.shutdown()

        return

    def start_domain(self, name):
        '''Start domain.'''

        domain = self.conn.lookupByName(name)
        domain.create()

        return

    def suspend_domain(self, domain):
        '''Suspend domain.'''

        domain.suspend()

        return

    def resume_domain(self, domain):
        '''Resume domain.'''

        domain.resume()

        return

    def traverse(self, tokens, tree):
        '''Auxiliary method for completion.'''

        if tree is None:

            return []

        elif len(tokens) == 0:

            return []

        if len(tokens) == 1:

            return [x + ' ' for x in tree if x.startswith(tokens[0])]

        else:
            if tokens[0] in tree.keys():
                
                return self.traverse(tokens[1:], tree[tokens[0]])

            else:

                return []

        return []


def main():
    '''Main function.'''

    vir_sh = PyVirsh()
    vir_sh.connect('qemu:///system')
    vir_sh.run_shell()

if __name__ == "__main__":

    main()
