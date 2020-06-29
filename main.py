"""This is a script to count matches of a pattern (bug) in another pattern (landscape)."""

import os
import re
import argparse
import collections

DATA_FOLDER_PATH = 'data'

ALPHANUM = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def escape(string, except_chars=''):
    """Escape all non-alphanumeric characters and the ones specified."""
    s = list(string)
    alphanum = ALPHANUM + except_chars
    for i, c in enumerate(string):
        if c not in alphanum:
            if c == "\000":
                s[i] = "\\000"
            else:
                s[i] = "\\" + c
    return string[:0].join(s)


class File(object):
    """Represents a file in the file system."""

    def __init__(self, filename):
        """
        Initialise object.

        :param filename: Name and extension of the file. (Ex: schnitzel.txt)
        :type filename: str
        """
        super(File, self).__init__()

        self.filename = filename

    @property
    def filename(self):
        """
        The filename with extension of the file.

        :type: str
        """
        return self._filename

    @filename.setter
    def filename(self, value):
        if not isinstance(value, str):
            raise TypeError('Filename should be string.')

        if not value.endswith('.txt'):
            raise TypeError('File should be in txt format.')

        self._filename = value

    @property
    def file_path(self):
        """
        The path of the provided file in the file system.

        :type: str
        """
        file_path = '{path}/{file}'.format(path=DATA_FOLDER_PATH, file=self.filename)

        if not os.path.exists(file_path):
            raise ValueError('Please make sure "{file_path}" exists.'.format(file_path=file_path))

        return file_path

    @classmethod
    def reader(cls, file_handler):
        """
        A generator method to return processed lines from a file handler.

        :param file_handler: File object opened to process.
        :type file_handler: BinaryIO

        :returns: Processed line
        :rtype: collections.Iterable[File.Line]
        """
        for line_id, pattern in enumerate(file_handler):
            pattern = pattern.rstrip()

            if pattern:
                yield cls.Line(line_id, pattern)

    class Line(object):
        def __init__(self, line_id, pattern):
            self.id = line_id
            self.pattern = pattern

        @property
        def id(self):
            """
            Id of the landscape line.

            :type: int
            """
            return self._id

        @id.setter
        def id(self, value):
            if not isinstance(value, int):
                raise TypeError('Id should be int.')

            self._id = value

        @property
        def pattern(self):
            """
            Pattern of the landscape line.

            :type: str
            """
            return self._pattern

        @pattern.setter
        def pattern(self, value):
            if not isinstance(value, str):
                raise TypeError('Pattern should be string.')

            self._pattern = value


class Bug(File):
    """Represents a bug pattern."""

    def __init__(self, filename):
        """
        Initialise object.

        :param filename: Name and extension of the file. (Ex: wurstel.txt)
        :type filename: str
        """
        super(Bug, self).__init__(filename)

        self._shape = None

        self._read_bug()

    @property
    def shape(self):
        """
        The shape representation of bug having each line as members of a list.

        :type: list
        """
        return self._shape

    @shape.setter
    def shape(self, value):
        if not isinstance(value, list):
            raise TypeError('Shape should be list.')

        self._shape = value

    def _read_bug(self):
        """Open the file representing bug and processes it."""
        with open(self.file_path, 'r') as file_handler:
            self.shape = [self.Part(line) for line in File.reader(file_handler)]

    class Part(File.Line):
        def __init__(self, line):
            """
            Initialise object.

            :param line: Line object representing bug part.
            :type line: Line
            """
            super(Bug.Part, self).__init__(line.id, line.pattern)

        @property
        def pattern(self):
            """
            Pattern of the bug part.

            :type: str
            """
            return self._pattern

        @pattern.setter
        def pattern(self, value):
            if not isinstance(value, str):
                raise TypeError('Pattern should be string.')

            self._pattern = self._format_pattern(value)

        @classmethod
        def _format_pattern(cls, pattern):
            """
            A method to convert bug ASCII characters into regular expression with lookahead.

            :param pattern: Pattern of the bug part.
            :type pattern: str

            :return: Regular expression
            :rtype: str
            """
            if not isinstance(pattern, str):
                raise TypeError('Pattern should be string.')

            if pattern:
                shape_part_first_char = escape(pattern[0])

                shape_part_rest_chars = escape(pattern[1:], except_chars=' ')
                shape_part_rest_chars = re.sub(r'\s+', cls._format_bug_replace_match_with_regex, shape_part_rest_chars)

                return '{first}(?={rest})'.format(first=shape_part_first_char, rest=shape_part_rest_chars)

        @classmethod
        def _format_bug_replace_match_with_regex(cls, match):
            """
            A method to replace match with a regular expression to look for any value with same length of match.

            Ex: If match is "apfelstrudel", it will be replaced with ".{12}"

            :param match: Match found from the regular expression used in "re.sub()".
            :type match: MatchObject

            :return: Regular expression
            :rtype: str
            """
            length_of_space = len(match.group(0))

            return '.{{{length}}}'.format(length=length_of_space)


class Landscape(File):
    """Represents a landscape pattern."""

    def __init__(self, filename):
        """
        Initialise object.

        :param filename: Name and extension of the file. (Ex: sachertorte.txt)
        :type filename: str
        """
        super(Landscape, self).__init__(filename)


class BugFinder(object):
    """Holds the operations to find bugs in a landscape."""

    def __init__(self, bug, landscape):
        """
        Initialise object.

        :param bug: Object representing bug pattern.
        :type bug: Bug
        :param landscape: Object representing landscape pattern.
        :type landscape: Landscape
        """
        self.bug = bug
        self.landscape = landscape

        self._bug_part_matches = collections.defaultdict(lambda: collections.defaultdict(list))
        self._bug_count = 0

    @property
    def bug(self):
        """
        Object representing bug pattern.

        :type: Bug
        """
        return self._bug

    @bug.setter
    def bug(self, value):
        if not isinstance(value, Bug):
            raise TypeError('Bug is either incorrect or not provided.')

        self._bug = value

    @property
    def landscape(self):
        """
        Object representing landscape pattern.

        :type: Landscape
        """
        return self._landscape

    @landscape.setter
    def landscape(self, value):
        if not isinstance(value, Landscape):
            raise TypeError('Landscape is either incorrect or not provided.')

        self._landscape = value
        self._bug_count = 0

    @property
    def bug_part_matches(self):
        """
        Hold occurrences of bug part matches in an ordered fashion. Is a default dict containing default dict of list.

        Ex: {line_number: {bug_part_id: [bug_part_match_position]}}

        :type: dict
        """
        return self._bug_part_matches

    @property
    def bug_count(self):
        """
        Number of times a bug is found in the landscape.

        :type: int
        """
        return self._bug_count

    def increment_bug_count(self):
        """Increment number of times a bug is found in the landscape by one."""
        self._bug_count += 1

    def bug_part_match_exists(self, bug_part, landscape_line):
        """
        Return whether a bug part match was registered in line.

        :param bug_part: Bug part to look for.
        :type bug_part: Bug.Part
        :param landscape_line: Line to look for bug part match in.
        :type landscape_line: File.line
        """
        if bug_part.id in self.bug_part_matches[landscape_line.id]:
            return True

        return False

    def register_bug_part_match(self, bug_part, landscape_line, bug_part_match_position):
        """
        When a bug part match is found, register it.

        The registrations are to be later checked with other bug part matches to determine
        whether registered bug part matches form a bug.
        
        :param bug_part: Bug part matched.
        :type bug_part: Bug.Part
        :param landscape_line: Line where the match is found in.
        :type landscape_line: File.Line
        :param bug_part_match_position: Match start position in line.
        :type bug_part_match_position: int
        """
        self.bug_part_matches[landscape_line.id][bug_part.id].append(bug_part_match_position)

    def deregister_bug_match(self, landscape_line, bug_part_match_position):
        """
        When a bug match is found, deregister individual bug part matches.

        This way found bugs later won't be used in checking for additional bugs. (Disallow conjoined twin bugs.)

        :param landscape_line: Line where the match of the last part of the bug is found in.
        :type landscape_line: File.Line
        :param bug_part_match_position: Match start position of the last part of bug in line.
        :type bug_part_match_position: int
        """
        landscape_line_number = landscape_line.id

        for bug_part in reversed(self.bug.shape):
            self.bug_part_matches[landscape_line_number][bug_part.id].remove(bug_part_match_position)

            landscape_line_number = landscape_line_number - 1

    def should_skip_all_bug_parts_in_line(self, bug_part, landscape_line):
        """
        Tell whether remaining bug part and remaining parts to check should be skipped.

        In the first -bug height amount- of lines, if no match for bug part found, skip remaining bug parts
        in the same line.

        :param bug_part: Bug part to check for.
        :type bug_part: Bug.Part
        :param landscape_line: Landscape line to check in.
        :type landscape_line: File.line
        :return: Whether to skip
        :rtype: bool
        """
        if landscape_line.id - bug_part.id <= 0:
            if not self.bug_part_match_exists(bug_part, landscape_line):
                return True

        return False

    def should_skip_bug_part_in_line(self, bug_part, landscape_line):
        """
        Tell whether bug part to check should be skipped.

        If previous bug part is not found in previous line, skip.

        :param bug_part: Bug part to check for.
        :type bug_part: Bug.Part
        :param landscape_line: Landscape line to check in.
        :type landscape_line: File.Line
        :return: Whether to skip
        :rtype: bool
        """
        if landscape_line.id - 1 >= 0 and bug_part.id - 1 >= 0:
            if bug_part.id - 1 not in self.bug_part_matches[landscape_line.id - 1]:
                return True

        return False

    def bug_part_match_belongs_to_a_bug(self, bug_part, landscape_line, bug_part_match_position):
        """
        Return whether bug part match is part of a bug.

        If the matched bug part is the last part of its shape, then checks whether previous parts exist in previous
        lines at the same match position.

        :param bug_part: Bug part to check for.
        :type bug_part: Bug.Part
        :param landscape_line: Landscape line to bug part match is found in.
        :type landscape_line: File.Line
        :param bug_part_match_position: Position of match in the line.
        :type bug_part_match_position: int
        :return: Whether bug part match is part of a bug.
        :rtype: bool
        """
        if bug_part.id == self.bug.shape[-1].id:
            landscape_line_number = landscape_line.id

            for bug_part in reversed(self.bug.shape[:-1]):
                landscape_line_number = landscape_line_number - 1

                if bug_part_match_position not in self.bug_part_matches[landscape_line_number][bug_part.id]:
                    return False

            return True

        return False

    def find_bug_part_and_bugs_in_landscape_line(self, bug_part, landscape_line):
        """
        Find bug part matches in landscape line.

        If a bug part mack is found, check whether it belongs to a bug.

        :param bug_part: Bug part to check for.
        :type bug_part: Bug.Part
        :param landscape_line: Landscape line to check bug part in.
        :type landscape_line: File.Line
        """
        for bug_part_match in re.finditer(bug_part.pattern, landscape_line.pattern):
            bug_part_match_position = bug_part_match.start()

            self.register_bug_part_match(bug_part, landscape_line, bug_part_match_position)

            if self.bug_part_match_belongs_to_a_bug(bug_part, landscape_line, bug_part_match_position):
                self.increment_bug_count()
                self.deregister_bug_match(landscape_line, bug_part_match_position)

    def find_bugs_in_landscape(self):
        """Loop through lines of the landscape to find bugs."""
        with open(self.landscape.file_path, 'r') as file_handler:
            for landscape_line in File.reader(file_handler):
                for bug_part in self.bug.shape:
                    if self.should_skip_bug_part_in_line(bug_part, landscape_line):
                        continue

                    self.find_bug_part_and_bugs_in_landscape_line(bug_part, landscape_line)

                    if self.should_skip_all_bug_parts_in_line(bug_part, landscape_line):
                        break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This is a script to count matches of a pattern (bug) in another pattern (landscape).'
    )

    parser.add_argument("--bug", "-b", help="filename with extension for bug")
    parser.add_argument("--landscape", "-l", help="filename with extension for landscape")

    args = parser.parse_args()

    if not args.bug:
        parser.print_usage()
        raise ValueError('Please provide a bug file.')

    if not args.landscape:
        parser.print_usage()
        raise ValueError('Please provide a landscape file.')

    bug_default = Bug(args.bug)
    landscape_default = Landscape(args.landscape)

    bug_finder = BugFinder(bug_default, landscape_default)
    bug_finder.find_bugs_in_landscape()

    print 'Bug count in the landscape: {count}'.format(count=bug_finder.bug_count)
