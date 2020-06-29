from unittest import TestCase, main
from main import escape, File, Bug, Landscape, BugFinder, DATA_FOLDER_PATH


class Test(TestCase):
    def test_escape(self):
        self.assertEqual(escape('north korea'), r'north\ korea')
        self.assertEqual(escape('north korea', except_chars=' '), r'north korea')


class TestFile(TestCase):
    def setUp(self):
        self.valid_filename = 'bug.txt'
        self.invalid_filenames = ['wrongFormat.doc', 123, -123, True, None, {}, []]
        self.non_existing_valid_filename = 'doesNotExist.txt'

    def test_File(self):
        self.assertEqual(File(self.valid_filename).filename, self.valid_filename)

        for filename in self.invalid_filenames:
            self.assertRaises(TypeError, lambda: File(filename))

    def test_file_path(self):
        f = File(self.non_existing_valid_filename)
        self.assertRaises(ValueError, lambda: f.file_path)

        f = File(self.valid_filename)
        self.assertEqual(f.file_path, '{folder}/{file}'.format(folder=DATA_FOLDER_PATH, file=self.valid_filename))

    def test_reader(self):
        f = File(self.valid_filename)

        with open(f.file_path, 'r') as file_handler:
            line_count = 0
            for line in File.reader(file_handler):
                self.assertIsInstance(line, File.Line)

                line_count += 1

            self.assertEqual(line_count, 3)


class TestLine(TestCase):
    def setUp(self):
        self.valid_line_prop = {'id': 1, 'pattern': '---'}
        self.invalid_line_props = [
            {'id': -123, 'pattern': -123},
            {'id': True, 'pattern': True},
            {'id': None, 'pattern': None},
            {'id': {}, 'pattern': {}},
            {'id': [], 'pattern': []},
        ]

    def test_Line(self):
        for line_prop in self.invalid_line_props:
            self.assertRaises(TypeError, lambda: File.Line(line_prop['id'], line_prop['pattern']))

    def test_id(self):
        line = File.Line(self.valid_line_prop['id'], self.valid_line_prop['pattern'])
        self.assertEqual(line.id, self.valid_line_prop['id'])

    def test_pattern(self):
        line = File.Line(self.valid_line_prop['id'], self.valid_line_prop['pattern'])
        self.assertEqual(line.pattern, self.valid_line_prop['pattern'])


class TestBug(TestCase):
    def setUp(self):
        self.valid_filename = 'bug.txt'
        self.invalid_filenames = ['wrongFormat.doc', 123, -123, True, None, {}, []]
        self.non_existing_valid_filename = 'doesNotExist.txt'

    def test_Bug(self):
        self.assertEqual(Bug(self.valid_filename).filename, self.valid_filename)

        for filename in self.invalid_filenames:
            self.assertRaises(TypeError, lambda: File(filename))

    def test__read_bug(self):
        bug = Bug(self.valid_filename)

        part_count = 0
        for part in bug.shape:
            self.assertIsInstance(part, Bug.Part)

            part_count += 1

        self.assertEqual(part_count, 3)


class TestPart(TestCase):
    def setUp(self):
        self.valid_filename = 'bug.txt'

    def test__format_bug(self):
        self.assertEqual(Bug.Part._format_pattern('data'), 'd(?=ata)')
        self.assertEqual(Bug.Part._format_pattern('da ta'), 'd(?=a.{1}ta)')
        self.assertEqual(Bug.Part._format_pattern('da  ta'), 'd(?=a.{2}ta)')
        self.assertEqual(Bug.Part._format_pattern('da t a'), 'd(?=a.{1}t.{1}a)')
        self.assertEqual(Bug.Part._format_pattern('da.t.a'), 'd(?=a\.t\.a)')

        self.assertRaises(TypeError, lambda: Bug.Part._format_pattern(123))
        self.assertRaises(TypeError, lambda: Bug.Part._format_pattern(True))
        self.assertRaises(TypeError, lambda: Bug.Part._format_pattern(None))
        self.assertRaises(TypeError, lambda: Bug.Part._format_pattern({}))
        self.assertRaises(TypeError, lambda: Bug.Part._format_pattern([]))

    def test__format_bug_replace_match_with_regex(self):
        bug = Bug(self.valid_filename)

        self.assertEqual(bug.shape[0].pattern, '\|(?=.{1}\|)')
        self.assertEqual(bug.shape[1].pattern, '\#(?=\#\#O)')


class TestLandscape(TestCase):
    def setUp(self):
        self.valid_filename = 'bug.txt'
        self.invalid_filenames = ['wrongFormat.doc', 123, -123, True, None, {}, []]

    def test_Landscape(self):
        self.assertEqual(Bug(self.valid_filename).filename, self.valid_filename)

        for filename in self.invalid_filenames:
            self.assertRaises(TypeError, lambda: File(filename))


class TestBugFinder(TestCase):
    def setUp(self):
        self.bug = Bug('bug.txt')
        self.landscape = Landscape('landscape.txt')

    def test_bug_and_landscape(self):
        bug_finder = BugFinder(self.bug, self.landscape)

        self.assertIsInstance(bug_finder.bug, Bug)
        self.assertIsInstance(bug_finder.landscape, Landscape)

        self.assertRaises(TypeError, lambda: BugFinder(123, None))

    def test_increment_bug_count(self):
        bug_finder = BugFinder(self.bug, self.landscape)
        bug_count = bug_finder.bug_count

        bug_finder.increment_bug_count()
        self.assertEqual(bug_finder.bug_count, bug_count + 1)

    def test_find_bugs_in_landscape(self):
        bug_finder = BugFinder(self.bug, self.landscape)
        bug_finder.find_bugs_in_landscape()

        self.assertEqual(bug_finder.bug_count, 3)


if __name__ == '__main__':
    main()
