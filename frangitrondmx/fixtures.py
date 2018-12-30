import json
from os import path


PROGRAM_TEMPLATE = """{
  "off": {
  }
}"""


def _indent(text, spaces=2):
    """Indents given text"""
    return '\n'.join([' ' * spaces + line for line in text.split('\n')])


def _doc(doc_item):
    """Helper to parse doc as list in JSON files"""
    if isinstance(doc_item, list):
        return "\n".join(doc_item)

    return doc_item


class Channel(object):

    def __init__(self, name):
        self.name = name
        self.number = 0
        self.role = ""
        self._doc = ""

    @staticmethod
    def from_dict(data):
        new_channel = Channel(data['name'])
        new_channel.role = data['role']
        new_channel._doc = _doc(data['doc'])
        return new_channel

    def doc(self, offset=0):
        doc = "CH {number:03d} [{name}] : {role}\n".format(
            number=self.number + offset,
            name=self.name,
            role=self.role
        )
        doc += _indent(self._doc)
        return doc

    def __repr__(self):
        return "<Channel(name='{name}', number={number}, role='{role}') at {id}>".format(
            name=self.name,
            number=self.number,
            role=self.role,
            id=id(self)
        )


class Fixture(object):

    def __init__(self, name):
        self.name = name
        self.caption = ""
        self.address = 1
        self.programs = dict()
        self.programs_filepath = None
        self._doc = ""
        self._indexed_mapping = list()
        self._named_mapping = dict()

    @staticmethod
    def from_dict(data):
        new_fixture = Fixture(data['name'])
        new_fixture.caption = data['caption']
        new_fixture._doc = _doc(data['doc'])

        mapping = data['mapping']
        mapping_len = max([int(chan) for chan in mapping.keys()]) + 1
        new_fixture._indexed_mapping = [None] * mapping_len

        for chan, chan_data in mapping.items():
            chan = int(chan)

            new_channel = Channel.from_dict(chan_data)
            new_channel.number = chan

            new_fixture._indexed_mapping[chan] = new_channel
            new_fixture._named_mapping[new_channel.name] = new_channel

        return new_fixture

    @staticmethod
    def from_folder(folder):
        filepath_definition = path.join(folder, 'definition.json')
        filepath_programs = path.join(folder, 'programs.json')

        with open(filepath_definition, 'r') as f_definition:
            definition = json.load(f_definition)

        new_fixture = Fixture.from_dict(definition)
        new_fixture.programs_filepath = filepath_programs
        new_fixture.reload_programs()

        return new_fixture

    def reload_programs(self):
        self.programs = dict()

        with open(self.programs_filepath, 'r') as f_programs:
            try:
                programs = json.load(f_programs)
            except ValueError:
                return

        for program_name, program_channels in programs.items():
            new_program = FixtureProgram.from_dict(program_name, program_channels)
            self.programs[program_name] = new_program

    def __getitem__(self, item):
        """Allows access to channels by number or by name"""
        if isinstance(item, int):
            return self._indexed_mapping[item]

        return self._named_mapping[item]

    def __getattr__(self, item):
        """Allows access to channels by name, as attribute"""
        return self._named_mapping[item]

    def channels(self):
        return self._indexed_mapping

    def channel_address(self, item):
        """Returns actual address of given channel, by index or name"""
        return self[item].number + self.address - 1

    def doc(self):
        doc = "{caption} [{name}]\n".format(
            caption=self.caption,
            name=self.name
        )
        doc += self._doc + '\n'

        channel_docs = [channel.doc(offset=self.address - 1) for channel in self.channels() if channel is not None]
        for channel_doc in channel_docs:
            doc += '\n'
            doc += _indent(channel_doc) + '\n'

        return doc

    def __repr__(self):
        doc = self._doc.split("\n")[0]
        return "<Fixture(name='{name}', doc='{doc}...', address={address} {channel_count} channels) at {id}>".format(
            name=self.name,
            doc=doc,
            address=self.address,
            channel_count=len(self._indexed_mapping) - 1,
            id=id(self)
        )


class FixtureProgram(object):
    def __init__(self, name):
        self.name = name
        self.caption = name.replace("_", " ")
        self.expressions = dict()

    @staticmethod
    def from_dict(name, channel_data):
        new_fixture_program = FixtureProgram(name)
        new_fixture_program.expressions = dict(channel_data)
        return new_fixture_program

    def __repr__(self):
        return "<FixtureProgram(name='{name}') at {id}>".format(
            name=self.name,
            id=id(self)
        )


if __name__ == '__main__':
    folder = "E:/PROJETS/dev/frangitron-dmx/frangitrondmx/fixtures/cameo-wookie-600b"
    fixture = Fixture.from_folder(folder)
    fixture.address = 20

    print fixture
    print fixture.channels()[1]
    print fixture.programs.values()[0]
    print ""
    print fixture.doc()
