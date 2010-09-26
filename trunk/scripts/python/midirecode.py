from MidiOutFile import MidiOutFile
from MidiInFile import MidiInFile
import sys

class Transposer(MidiOutFile):
    
    "Recode sequence_name"
    
    def __init__(self, raw_out='', from_enc='sjis', to_enc='gbk'):
        MidiOutFile.__init__(self, raw_out)
        self.from_enc = from_enc
        self.to_enc = to_enc

    def sequence_name(self, text):
        """
        Sequence/track name
        text: string
        """
        try:
            text = text.decode(self.from_enc).encode(self.to_enc)
        except UnicodeDecodeError:
            print >> sys.stderr, 'Error decoding', text
            pass
        except UnicodeEncodeError:
            text = text.decode(self.from_enc).encode(self.to_enc, 'replace')
            text = text.replace('?', '_')
        MidiOutFile.sequence_name(self, text)

    def sysex_event(self, data):
        MidiOutFile.system_exclusive(self, data)


if __name__ == '__main__':
    import sys, os.path, glob
    if len(sys.argv) != 4:
        print 'MIDI song title renamer'
        print 'Usage: %s midi_file from_enc to_enc' % (os.path.basename(sys.argv[0]),)
        print 'Example: %s test.mid cp932 gbk' % (os.path.basename(sys.argv[0]),)
        print 'The output file is midi_file.new. midi_file can have wildcard'
        sys.exit(0)

    for fname in glob.glob(unicode(sys.argv[1])):
        print 'Processing', fname
        midi_out = Transposer(fname + '.new',
                sys.argv[2], sys.argv[3])

        midi_in = MidiInFile(midi_out, fname)
        midi_in.read()
