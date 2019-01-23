# (c) 2018 Dean Stamler

import logging, json, constants
import inference
from datetime import datetime
import random, string

class InventoryLogFile(object):
    """Wrapper for a log file"""
    def __init__(self, f):
        self.log = logging.getLogger(__name__)
        try:
            self.filehandle = open(f)
        except ValueError:
            self.log.error("Failed to open {}".format(f))

        self.version, self.regex = self._get_version()
        self.load_file()
        self.client_ids = []

    def close_file(self):
        self.filehandle.close()

    # Determine file format version and load appropriate regex
    def _get_version(self):
        first_line = self.filehandle.readline()
        self.filehandle.seek(0)
        version = regex = None
        for v in constants.Version:
            regex = getattr(constants, 'full_line_' + v.name)
            if (regex.match(first_line)):
                self.log.debug("log file version %s", v.name)
                version = v
                break
        if(version is None):
            msg = "Unable to determine version of {}".format(self.filehandle.name)
            raise ValueError(msg)
        return version, regex

    def _disambiguate_dates_in_context(self, line_objects):
        # Infer the value of an ambiguous date entry by comparing it to the
        # last and next unambiguous datetime objects in the list and choosing
        # the one that is between them.
        # If both options work, pick the earliest one.
        # If there is no lower bound, pick the latest choice.
        # If there is no upper bound, pick the earliest choice.

        lower_bound = upper_bound = None  # datetime objects
        span = 0    # number of ambiguous datetime strings counted in this area
        list_length = len(line_objects)
        idx = 0 # along with t, the indices between which dates are ambiguous

        for i, line_object in enumerate(line_objects):

            if ('datetime' in line_object):
                # This line_object is unambiguous because it has a datetime
                if (span > 0):
                    # since the last line_object was ambiguous, make this
                    # one the upper bound and infer the one or more ambiguous
                    # dates within the bounds
                    upper_bound = line_object['datetime']
                    t = idx + span
                    line_objects[idx:t] = self._unwrap_process_rewrap(lower_bound,
                                                upper_bound, line_objects[idx:t])

                    # Now that all previous dates are unambiguous make this
                    # the new lower_bound
                    lower_bound = line_object['datetime']
                    span = 0
                else:
                    # since the last line_object was unambiguous, make this
                    # one the new lower_bound and continue
                    lower_bound = line_object['datetime']
            else:
                # This line_object is ambiguous because it has no datetime;
                # Add its index to the list of ambiguous indices
                if (span == 0):
                    idx = i
                span += 1
                if (i == list_length - 1):
                    # The last item is ambiguous so we need to clean up the end
                    t = idx + span
                    line_objects[idx:t] = self._unwrap_process_rewrap(lower_bound,
                                                upper_bound, line_objects[idx:t])
        return line_objects

    def _load_datetime(self, obj,regex_match):
        match_obj = None
        for k, v in constants.date_formats.items():
            match_obj = v[0].match(regex_match.group(1))
            if (match_obj is not None):
                if (k == 'ambiguous_date'):
                    obj['raw_date_string'] = regex_match.group(1)
                    return obj, 1
                else:
                    obj['datetime'] = datetime.strptime(regex_match.group(1),v[1])
                    return obj, 0
        if(match_obj is None):
            raise ValueError("Unable to determine format of "
                                "date string '{}'.".format(regex_match.group(1)))

    def load_file(self):

        # Build the list of line objects, counting ambiguous dates
        lines = []
        ambiguous_date_count = 0
        for line in self.filehandle:
            regex_match = self.regex.match(line)
            obj = {}#{'line':line.rstrip()}
            obj['username'] = regex_match.group(2).lower()
            obj['manufacturer'] = regex_match.group(3)
            obj['serial'] = regex_match.group(4).strip()
            # The SLUG code in firebase cloud function rawLogins:
            # serial.trim() + ',' + mfg.toLowerCase().replace('.','').replace(',','').replace('inc','').replace('ltd','').trim().replace(' ','_');
            obj['slug'] = obj['serial'] +','+ obj['manufacturer'].lower().replace('.','').replace(',','').replace('inc','').replace('ltd','').strip().replace(' ','_')
            obj['computer_name'] = regex_match.group(5)
            if(self.version > constants.Version.v3):
                obj['network_config'] = json.loads(regex_match.group(6))
            if(self.version == constants.Version.v3):
                obj['network_config'] = [{'macaddress':regex_match.group(6),'ipaddresses':regex_match.group(12).split(',')}]
            if(self.version > constants.Version.v1):
                obj['ram'] = regex_match.group(7)
                obj['os_version'] = regex_match.group(8)
                obj['os_sku'] = regex_match.group(9)
                obj['os_arch'] = regex_match.group(10)
                obj['hdd'] = regex_match.group(11)
            if(self.version < constants.Version.v3):
                obj['network_config'] = [{'macaddress':regex_match.group(6)}]
                obj, zero_or_one_ambiguous_dates = self._load_datetime(obj,regex_match)
            else:
                obj['datetime'] = datetime.strptime(regex_match.group(1),'%Y-%m-%d %H:%M:%S')
                zero_or_one_ambiguous_dates = 0

            ambiguous_date_count += zero_or_one_ambiguous_dates
            lines.append(obj)

        # We now have a list of line objects which are dicts. Each dict contains
        # a copy of the line, parsed variables for each entry, and if the date was
        # unambiguous, a datetime object. Now we go through this list and infer
        # the value of ambiguous dates if there are any.
        if (ambiguous_date_count > 0):
            self.log.debug("Detected {} ambiguous dates in {} lines of {}"
                    "".format(ambiguous_date_count,len(lines), self.filehandle.name))
            lines = self._disambiguate_dates_in_context(lines)

        self.log.debug("Loaded %s lines.", len(lines))
        self.lines = lines

    def _unwrap_process_rewrap(self, lower_bound, upper_bound, line_objects):
        s = [obj['raw_date_string'] for obj in line_objects]
        datetime_list = inference.infer(lower_bound, upper_bound, s)
        for idx, line_object in enumerate(line_objects):
            line_object['datetime'] = datetime_list[idx]
            del(line_object['raw_date_string'])
        return line_objects

    def to_json(self):
        if len(self.lines) == 1:
            # return a dict rather than a list for one line
            return json.dumps(self.lines[0], default=str, separators=(',', ':'))

        for line in self.lines:
            # Add a client_id to each item in the list
            line['client_id'] = ''.join(random.choice(string.ascii_uppercase) for _ in range(16))
            self.client_ids.append(line['client_id'])
        return json.dumps(self.lines, default=str, separators=(',', ':'))
    
    def to_json_api_obj(self):
        if len(self.lines) == 1:
            # return a dict rather than a list for one line
            resource = { "type": "RawLogins", "attributes": self.lines[0] }
            return resource
        
        resources = []
        for line in self.lines:
            # return a list of dicts. TODO: validate client_id, although this may be a breaking line
            line['client_id'] = ''.join(random.choice(string.ascii_uppercase) for _ in range(16))
            self.client_ids.append(line['client_id'])
            resources.append({ "type": "RawLogins", "attributes": line })
        return resources
