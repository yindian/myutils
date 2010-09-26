"""
This is a DBF reader which reads Visual Fox Pro DBF format with Memo field.

Usage:
    rec = readDbf('test.dbf')
    for line in rec:
        print line['name']

@author Yusdi Santoso
@date 13/07/2007

yindian modified for decryption support on 2010/09/25
                 for field type unpack  on 2010/09/26 (not thoroughly tested)
"""
import struct
import os, os.path
import sys
import csv
import tempfile
import ConfigParser

class Dbase:
    def __init__(self):
        self.fdb = None
        self.fmemo = None
        self.db_data = None
        self.memo_data = None
        self.fields = None
        self.num_records = 0
        self.header = None
        self.memo_file = ''
        self.memo_header = None
        self.memo_block_size = 0
        self.memo_header_len = 0

    def _drop_after_NULL(self, txt):
        for i in range(0, len(txt)):
            if ord(struct.unpack('c', txt[i])[0])==0:
                return txt[:i]
        return txt 

    def _reverse_endian(self, num):
        if not len(num):
            return 0
        val = struct.unpack('<L', num)
        val = struct.pack('>L', val[0])
        val = struct.unpack('>L', val)
        return val[0]

    def _timestamp_to_ymdhms(self, julianday, milliseconds):
        x2 = julianday - 1721120 #1721119.5
        c2 = int((4*x2 + 3)/146097.)
        x1 = x2 - int(146097*c2/4.)
        c1 = int((100*x1 + 99)/36525.)
        x0 = x1 - int(36525*c1/100.)
        j  = 100*c2 + c1
        m  = int((5*x0 + 461)/153.)
        d  = x0 - int((153*m - 457)/5.) + 1
        if m > 12:
            m -= 12
            j += 1
        hr = int(milliseconds / 3600000)
        milliseconds -= hr * 3600000
        mn = int(milliseconds / 60000)
        milliseconds -= mn * 60000
        sc = int(milliseconds / 1000)
        return (j, m, d, hr, mn, sc)

    def _assign_ids(self, lst, ids):
        result = {}
        idx = 0
        for item in lst:
            id = ids[idx]
            result[id] = item
            idx += 1
        return result

    def open(self, db_name, unpackfields=False, memodecrypt=None, maxrec=0):
        filesize = os.path.getsize(db_name)
        if filesize <= 68:
            raise IOError, 'The file is not large enough to be a dbf file'

        self.fdb = open(db_name, 'rb')

        self.memo_file = ''
        if os.path.isfile(db_name[0:-1] + 't'):
            self.memo_file = db_name[0:-1] + 't'
        elif os.path.isfile(db_name[0:-3] + 'fpt'):
            self.memo_file = db_name[0:-3] + 'fpt'

        if self.memo_file:    
            #Read memo file
            self.fmemo = open(self.memo_file, 'rb')
            self.memo_data = self.fmemo.read()
            self.memo_header = self._assign_ids(struct.unpack('>6x1H', self.memo_data[:8]), ['Block size'])
            self.memo_decrypt = memodecrypt
            block_size = self.memo_header['Block size']
            if not block_size:
                block_size = 512
            self.memo_block_size = block_size
            self.memo_header_len = block_size
            memo_size = os.path.getsize(self.memo_file)

        #Start reading data file
        data = self.fdb.read(32)
        self.header = self._assign_ids(struct.unpack('<B 3B L 2H 20x', data), ['id', 'Year', 'Month', 'Day', '# of Records', 'Header Size', 'Record Size'])
        if maxrec > 0 and self.header['# of Records'] > maxrec:
            self.header['# of Records'] = maxrec
        self.header['id'] = hex(self.header['id'])

        self.num_records = self.header['# of Records']
        data = self.fdb.read(self.header['Header Size']-34)
        self.fields = {}
        self.fields_unpack = unpackfields
        x = 0
        header_pattern = '<11s c 4x B B 14x'
        ids = ['Field Name', 'Field Type', 'Field Length', 'Field Precision']
        pattern_len = 32
        for offset in range(0, len(data), 32):
            if ord(data[offset])==0x0d:
                break
            x += 1
            data_subset = data[offset: offset+pattern_len]
            if len(data_subset) < pattern_len:
                data_subset += ' '*(pattern_len-len(data_subset))
            self.fields[x] = self._assign_ids(struct.unpack(header_pattern, data_subset), ids)
            self.fields[x]['Field Name'] = self._drop_after_NULL(self.fields[x]['Field Name'])

        self.fdb.read(3)
        if self.header['# of Records']:
            data_size = (self.header['# of Records'] * self.header['Record Size']) - 1
            self.db_data = self.fdb.read(data_size)
        else:
            self.db_data = ''
        self.row_format = '<'
        self.row_ids = []
        self.row_len = 0
        for key in self.fields:
            field = self.fields[key]
            self.row_format += '%ds ' % (field['Field Length'])
            self.row_ids.append(field['Field Name'])
            self.row_len += field['Field Length']

    def close(self):
        if self.fdb:
            self.fdb.close()
        if self.fmemo:
            self.fmemo.close()

    def get_numrecords(self):
        return self.num_records

    def get_record_with_names(self, rec_no):
        """
        This function accept record number from 0 to N-1
        """
        if rec_no < 0 or rec_no > self.num_records:
            raise Exception, 'Unable to extract data outside the range' 

        offset = self.header['Record Size'] * rec_no
        data = self.db_data[offset:offset+self.row_len]
        record = self._assign_ids(struct.unpack(self.row_format, data), self.row_ids)

        if self.memo_file:
            for key in self.fields:
                field = self.fields[key]
                f_type = field['Field Type']
                f_name = field['Field Name']
                c_data = record[f_name]

                if f_type=='M' or f_type=='G' or f_type=='B' or f_type=='P':
                    try:
                        c_data = self._reverse_endian(c_data)
                    except:
                        c_data = int(c_data)
                    if c_data:
                        record[f_name] = self.read_memo(c_data-1).strip()
                #else:
                #    record[f_name] = c_data.strip()
        if self.fields_unpack:
            # Caution: not-tested code. no warranty at all
            for key in self.fields:
                field = self.fields[key]
                f_type = field['Field Type']
                f_name = field['Field Name']
                f_leng = field['Field Length']
                f_prec = field['Field Precision']
                c_data = record[f_name]
                if f_type == 'N':                       # Number
                    assert f_leng <= 18
                    if f_prec == 0:
                        record[f_name] = int(c_data)
                    else:
                        record[f_name] = float(c_data)
                elif f_type == 'L':                     # Logical
                    assert f_leng == 1
                    if c_data in 'YyTt':
                        record[f_name] = True
                    elif c_data in 'NnFf':
                        record[f_name] = False
                    else:
                        assert c_data == '?'
                        record[f_name] = None
                elif f_type == 'D':                     # Date in YYYYMMDD
                    assert f_leng == 8
                    record[f_name] = (int(c_data[:4]), int(c_data[4:6]),
                            int(c_data[6:]))
                elif f_type == 'F':                     # Floating point
                    assert f_leng == 20
                    record[f_name] = float(c_data)
                elif f_type == 'I' or f_type == '+':    # Integer, Autoincrement
                    assert f_leng == 4
                    record[f_name] = struct.unpack('<l', c_data)[0]
                elif f_type == 'V' or f_type == 'X':    # Varchar
                    len = ord(c_data[-1])
                    if len < f_leng and c_data[len:-1].strip() == '':
                        record[f_name] = c_data[:len]
                elif f_type == '@' or f_type == 'T':    # Timestamp, DateTime
                    assert f_leng == 8
                    date = struct.unpack('<l', c_data[:4])[0]
                    time = struct.unpack('<l', c_data[4:])[0]
                    record[f_name] = self._timestamp_to_ymdhms(date, time)
                elif f_type == 'O':                     # Double
                    assert f_leng == 8
                    record[f_name] = struct.unpack('d', c_data)[0]
                elif f_type == 'Y':                     # Currency
                    assert f_leng == 8
                    record[f_name] = struct.unpack('<q', c_data)[0] / 10000.

        return record

    def read_memo_record(self, num, in_length):
        """
        Read the record of given number. The second parameter is the length of
        the record to read. It can be undefined, meaning read the whole record,
        and it can be negative, meaning at most the length
        """
        if in_length < 0:
            in_length = -self.memo_block_size

        offset = self.memo_header_len + num * self.memo_block_size
        self.fmemo.seek(offset)
        if in_length<0:
            in_length = -in_length
        if in_length==0:
            return ''
        return self.fmemo.read(in_length)    
    
    def read_memo(self, num):
        offset = self.memo_header_len + num * self.memo_block_size
        buffer = self.memo_data[offset:offset+8]
        if len(buffer)<8:
            return ''
        length = struct.unpack('>L', buffer[4:4+4])[0] + 8

        buffer = self.memo_data[offset+8:offset+length]
        if self.memo_decrypt is not None:
            buffer = self.memo_decrypt(buffer)
        return buffer

def readDbf(filename, unpackfields=False, memodecrypt=None, maxrec=0):
    """
    Read the DBF file specified by the filename and 
    return the records as a list of dictionary.
    @param filename File name of the DBF
    @return List of rows
    """
    db = Dbase()
    db.open(filename, unpackfields=unpackfields, memodecrypt=memodecrypt, maxrec=maxrec)
    num = db.get_numrecords()
    rec = []
    for i in range(0, num):
        record = db.get_record_with_names(i)
        rec.append(record)    
    db.close()
    del db
    return  rec

if __name__=='__main__':
    rec = readDbf('dbf/sptable.dbf')
    for line in rec:
        print '%s %s' % (line['GENUS'].strip(), line['SPECIES'].strip())
