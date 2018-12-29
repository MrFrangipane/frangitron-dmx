

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
        doc = "Channel {number:03d} (.{name}) : {role}\n".format(
            number=self.number + offset,
            name=self.name,
            role=self.role
        )
        doc += self._doc
        return doc

    def __repr__(self):
        return "<(Channel name='{name}', number={number}, role='{role}')>".format(
            name=self.name,
            number=self.number,
            role=self.role
        )


class Fixture(object):

    def __init__(self, name):
        self.name = name
        self.address = 1
        self._doc = ""
        self._indexed_mapping = list()
        self._named_mapping = dict()

    @staticmethod
    def from_dict(data):
        new_fixture = Fixture(data['name'])
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

    def doc(self):
        doc = self.name + '\n'
        doc += self._doc + '\n'

        channel_docs = [channel.doc(offset=self.address - 1) for channel in self.channels() if channel is not None]
        for channel_doc in channel_docs:
            doc += '\n'
            doc += _indent(channel_doc) + '\n'

        return doc

    def __repr__(self):
        doc = self._doc.split("\n")[0]
        return "<Fixture(name='{name}', doc='{doc}...', {channel_count} channels)>".format(
            name=self.name,
            doc=doc,
            channel_count=len(self._indexed_mapping) - 1
        )

if __name__ == '__main__':
    import json
    with open("E:/PROJETS/dev/frangitron-dmx/frangitrondmx/fixtures/cameo-wookie-600b.json", "r") as f_fixture:
        data = json.load(f_fixture)

    fixture = Fixture.from_dict(data)
    fixture.address = 20
    print fixture.doc()
