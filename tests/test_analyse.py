import os
import unittest

from mock import Mock, patch

from dls_powerpmacanalyse import dls_ppmacanalyse


class DummyPpmac:
    def __init__(self):
        self.source = "unknown"
        self.Pvariables = ["var"]
        self.Ivariables = ["var"]
        self.Mvariables = ["var"]
        self.Qvariables = ["var"]
        self.dataStructures = {
            "test": dls_ppmacanalyse.PowerPMAC().DataStructure(
                "test",
                "test",
                "test",
                "test",
                "test",
                "test",
                "test",
                "test",
                "test",
                "test",
                "test",
                "test",
                "test",
                "test",
            )
        }
        self.activeElements = {
            "test": dls_ppmacanalyse.PowerPMAC().ActiveElement("test", "testval")
        }
        self.coordSystemDefs = {
            "test": dls_ppmacanalyse.PowerPMAC().CoordSystemDefinition(csNumber=1)
        }
        self.motionPrograms = {
            "motionProgram": dls_ppmacanalyse.PowerPMAC().Program("", "", 3, "", "")
        }
        self.subPrograms = {}
        self.plcPrograms = {}
        self.forwardPrograms = {}
        self.inversePrograms = {}


class DummyProj:
    class File:
        def __init__(self):
            self.contents = ["Test"]

    def __init__(self):
        self.files = {
            "file1": self.File(),
            "file2": self.File(),
        }

        self.source = "repository"


class DummyPpmacArgs:
    def __init__(self):
        self.interface = None
        self.backup = None
        self.compare = ["all", "test1", "test2"]
        self.recover = None
        self.download = None
        self.resultsdir = None
        self.username = "root"
        self.password = "deltatau"
        self.name = None


class TestPpmacLexer(unittest.TestCase):
    def test_scanNonAlphaNumeric(self):
        charsInput = "dfkk ="
        obj = dls_ppmacanalyse.PPMACLexer(charsInput)
        lex_res = obj.scanNonAlphaNumeric("=", obj.chars)
        assert lex_res == "="

    def test_scanNumber(self):
        charsInput = "dfjfj=-88"
        obj = dls_ppmacanalyse.PPMACLexer(charsInput)
        lex_res = obj.scanNumber("8", obj.chars)
        assert lex_res == "8"
        lex_res = obj.scanNumber("2", obj.chars)
        assert lex_res == "2"

    def test_scanSymbol(self):
        charsInput = "callsub pv0"
        obj = dls_ppmacanalyse.PPMACLexer(charsInput)
        lex_res = obj.scanSymbol("callsub", obj.chars)
        assert lex_res == "callsub"

    def test_scanSymbolQuote(self):
        charsInput = "'dfdf'"
        obj = dls_ppmacanalyse.PPMACLexer(charsInput)
        lex_res = obj.scanSymbol("'", obj.chars)
        assert lex_res == "'"

    def test_scanHexadecimal(self):
        charsInput = "$00000001"
        obj = dls_ppmacanalyse.PPMACLexer(charsInput)
        lex_res = obj.scanSymbol("$", obj.chars)
        assert lex_res == "$"

    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACLexer.scanHexadecimal")
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACLexer.scanString")
    def test_lex(self, mock_string, mock_hex):
        charsInput = "$00000001 'test' 2 ="
        obj = dls_ppmacanalyse.PPMACLexer(charsInput)
        obj.lex(obj.chars)
        mock_hex.assert_called_with("$", obj.chars)
        mock_string.assert_called_with("'", obj.chars)


# def test_init(self):
# def test_lex(self):
# def test_scanSymbol(self):


class TestPpmacParser(unittest.TestCase):
    def test_parser(self):
        with patch(
            "sys.argv", ["dls-powerpmac-analyse", "-b", "all", "-i", "192.168.0.1:22"]
        ):
            ppmacArgs = dls_ppmacanalyse.parseArgs()
            assert ppmacArgs.interface == ["192.168.0.1:22"]
            assert ppmacArgs.backup == ["all"]


class TestPpmacProject(unittest.TestCase):
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACProject.buildProjectTree")
    def setUp(self, mock_build_tree):
        test_source = "repository"
        test_root = "/tmp"
        self.obj = dls_ppmacanalyse.PPMACProject(test_source, test_root)

    def test_init(self):
        assert self.obj.root == "/tmp"
        assert self.obj.source == "repository"
        assert self.obj.files == {}
        assert self.obj.dirs == {}

    def test_getFileContents(self):
        test_file = "/tmp/test.txt"
        with open(test_file, "w") as f:
            f.write("test\n")
        ret = self.obj.getFileContents("test.txt")
        assert ret == ["test\n"]
        os.remove(test_file)


class TestPpmacProjectCompare(unittest.TestCase):
    def setUp(self):
        self.mockA = Mock()
        self.mockB = Mock()
        self.obj = dls_ppmacanalyse.ProjectCompare(self.mockA, self.mockB)

    def test_init(self):
        assert self.obj.projectA == self.mockA
        assert self.obj.projectB == self.mockB
        assert self.obj.filesOnlyInA == {}
        assert self.obj.filesOnlyInB == {}
        assert self.obj.filesInAandB == {}

    def test_set_projA(self):
        mock_proj = Mock()
        self.obj.setProjectA(mock_proj)
        assert self.obj.projectA == mock_proj

    def test_set_projB(self):
        mock_proj = Mock()
        self.obj.setprojectB(mock_proj)
        assert self.obj.projectB == mock_proj

    def test_compare_proj_files(self):
        test_file = "/tmp/test_diff.txt"
        with open(test_file, "w") as f:
            pass
        self.obj.projectA = DummyProj()
        self.obj.projectB = DummyProj()
        self.obj.compareProjectFiles("/tmp/test_diff.txt")
        assert self.obj.filesOnlyInA == {}
        assert self.obj.filesOnlyInB == {}
        f = open(test_file, "r")
        assert f.read() == ""
        f.close()
        os.remove(test_file)


class TestPpmacCompare(unittest.TestCase):
    def setUp(self):
        self.mockA = DummyPpmac()
        self.mockB = DummyPpmac()
        self.mockA.source = "DummyPmacA"
        self.mockB.source = "DummyPmacB"
        self.obj = dls_ppmacanalyse.PPMACCompare(
            self.mockA, self.mockB, "./ppmacAnalyse"
        )
        self.obj.compareDir = "/tmp"

    def test_init(self):
        assert self.obj.ppmacInstanceA == self.mockA
        assert self.obj.ppmacInstanceB == self.mockB
        assert self.obj.elemNamesOnlyInA == {}
        assert self.obj.elemNamesOnlyInB == {}
        assert self.obj.elemNamesInAandB == {}
        assert self.obj.activeElemsOnlyInA == {}
        assert self.obj.activeElemsOnlyInB == {}
        assert self.obj.activeElemsInAandB == {}

    def test_set_projA(self):
        mock_proj = Mock()
        self.obj.setPPMACInstanceA(mock_proj)
        assert self.obj.ppmacInstanceA == mock_proj

    def test_set_projB(self):
        mock_proj = Mock()
        self.obj.setPPMACInstanceB(mock_proj)
        assert self.obj.ppmacInstanceB == mock_proj

    def test_compareActiveElementsSame(self):
        activeDir = self.obj.compareDir + "/active"
        activeFilename = activeDir + "/ActiveElements_diff.html"
        self.obj.compareActiveElements()
        f = open(activeFilename, "r+")
        assert "No Differences Found" in f.read()
        f.close()
        os.remove(activeFilename)
        os.rmdir(activeDir)

    def test_compareActiveElementsAOnly(self):
        self.obj.ppmacInstanceA.activeElements[
            "test2"
        ] = dls_ppmacanalyse.PowerPMAC().ActiveElement("test", "testval")
        activeDir = self.obj.compareDir + "/active"
        activeFilenameHtml = activeDir + "/ActiveElements_diff.html"
        activeFilename = activeDir + "/test.diff"
        self.obj.compareActiveElements()
        f = open(activeFilename, "r+")
        assert (
            f.read() == "@@ Active elements in source 'DummyPmacA' but not source"
            " 'DummyPmacB' @@\n>>>> test = testval\n"
        )
        f.close()
        os.remove(activeFilename)
        os.remove(activeFilenameHtml)
        os.rmdir(activeDir)

    def test_compare_programs_same(self):
        self.obj.comparePrograms()
        assert self.obj.progNamesInAandB == {"motionProgram"}
        assert len(self.obj.progNamesOnlyInA) == 0

    def test_compare_programs_diff(self):
        self.obj.ppmacInstanceA.subPrograms[
            "subPrograms"
        ] = dls_ppmacanalyse.PowerPMAC().Program("", "", 3, "", "")
        activeDir = self.obj.compareDir + "/active/programs"
        activeFilenameHtml = activeDir + "/MissingPrograms.html"
        activeFilename = activeDir + "/missingPrograms.txt"
        self.obj.comparePrograms()
        assert self.obj.progNamesInAandB == {"motionProgram"}
        assert len(self.obj.progNamesOnlyInA) == 1
        f = open(activeFilename, "r+")
        assert (
            "@@ Programs in source 'DummyPmacA' but not source"
            " 'DummyPmacB'\n>>>> subPrograms\n" in f.read()
        )
        f.close()
        os.remove(activeFilename)
        os.remove(activeFilenameHtml)
        os.rmdir(activeDir)

    def test_compareCoOrdSysDefsSame(self):
        self.obj.compareCoordSystemAxesDefinitions()
        assert self.obj.coordSystemsInAandB == {"test"}
        assert len(self.obj.progNamesOnlyInA) == 0

    def test_compareCoOrdSysDefsDiff(self):
        self.obj.ppmacInstanceA.coordSystemDefs[
            "test2"
        ] = dls_ppmacanalyse.PowerPMAC().CoordSystemDefinition(csNumber=2)
        activeDir = self.obj.compareDir + "/active/axes"
        activeFilenameHtml = activeDir + "/MissingCoordSystems.html"
        activeFilename = activeDir + "/missingCoordSystems.txt"
        self.obj.compareCoordSystemAxesDefinitions()
        assert len(self.obj.coordSystemsInAandB) == 1
        assert len(self.obj.progNamesOnlyInA) == 0
        f = open(activeFilename, "r+")
        assert (
            "@@ Coordinate Systems defined in source 'DummyPmacA'"
            " but not source 'DummyPmacB'\n>>>> &test2" in f.read()
        )
        f.close()
        os.remove(activeFilename)
        os.remove(activeFilenameHtml)
        os.rmdir(activeDir)


class TestPpmacRepositoryWriteRead(unittest.TestCase):
    def setUp(self):
        self.mock_ppmac = DummyPpmac()
        self.obj = dls_ppmacanalyse.PPMACRepositoryWriteRead(
            self.mock_ppmac, "./ppmacAnalyse"
        )

    def test_init(self):
        assert self.obj.ppmacInstance == self.mock_ppmac
        assert self.obj.ppmacInstance.source == "repository"
        assert self.obj.repositoryPath == "./ppmacAnalyse"

    def test_setPPMACInstance(self):
        mock_ppmac = DummyPpmac()
        self.obj.setPPMACInstance(mock_ppmac)
        assert self.obj.ppmacInstance == mock_ppmac
        assert self.obj.ppmacInstance.source == "repository"

    def test_setRepositoryPath(self):
        test_path = os.getcwd()
        self.obj.setRepositoryPath(test_path)
        assert self.obj.repositoryPath == test_path

    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACRepositoryWriteRead"
        ".writeAllPrograms"
    )
    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACRepositoryWriteRead"
        ".writeActiveElements"
    )
    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACRepositoryWriteRead."
        "writeDataStructures"
    )
    def test_writeActiveState(self, mock_write, mock_write_active, mock_write_all):
        self.obj.writeActiveState()
        assert mock_write.called
        assert mock_write_active.called
        assert mock_write_all.called

    def test_writeDataStructures(self):
        test_file = "/tmp/active/dataStructures.txt"
        test_dir = "/tmp/active/"
        self.obj.repositoryPath = "/tmp"
        os.makedirs(test_dir, exist_ok=True)
        self.obj.writeDataStructures()
        f = open(test_file, "r+")
        assert (
            f.read() == "test, test, test, test, test, test, test, test, test, "
            "test, test, test, test, test\n"
        )
        f.close()
        os.remove(test_file)
        os.rmdir(test_dir)

    def test_writeActiveElements(self):
        test_file = "/tmp/active/activeElements.txt"
        test_dir = "/tmp/active/"
        self.obj.repositoryPath = "/tmp"
        os.makedirs(test_dir, exist_ok=True)
        self.obj.writeActiveElements()
        f = open(test_file, "r+")
        assert f.read() == "test  testval\n"
        f.close()
        os.remove(test_file)
        os.rmdir(test_dir)

    # def test_readAndStoreBufferedPrograms(self):


class TestPpmacHardwareWriteRead(unittest.TestCase):
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead.readSysMaxes")
    def setUp(self, mock_readsys):
        self.mock_ppmac = DummyPpmac()
        self.obj = dls_ppmacanalyse.PPMACHardwareWriteRead(self.mock_ppmac)

    def test_init(self):
        assert self.obj.ppmacInstance == self.mock_ppmac
        assert self.obj.ppmacInstance.source == "hardware"
        assert self.obj.pp_swtbl0_txtfile == "pp_swtbl0.txt"
        assert self.obj.pp_swtlbs_symfiles == [
            "pp_swtbl1.sym",
            "pp_swtbl2.sym",
            "pp_swtbl3.sym",
        ]

    def test_setPPMACInstance(self):
        mock_ppmac = DummyPpmac()
        self.obj.setPPMACInstance(mock_ppmac)
        assert self.obj.ppmacInstance == mock_ppmac
        assert self.obj.ppmacInstance.source == "hardware"

    def test_getCommandReturnInt(self):
        dls_ppmacanalyse.sshClient = Mock()
        attrs = {"sendCommand.return_value": ("0", True)}
        dls_ppmacanalyse.sshClient.configure_mock(**attrs)
        assert self.obj.getCommandReturnInt("cmd") == 0
        dls_ppmacanalyse.sshClient.sendCommand.assert_called_with("cmd")

    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "getCommandReturnInt"
    )
    def test_readSysMaxes(self, mock_getint):
        mock_getint.return_value = 1
        self.obj.readSysMaxes()
        assert mock_getint.call_count == 6
        assert self.obj.ppmacInstance.numberOfMotors == 1
        assert self.obj.ppmacInstance.numberOfCoordSystems == 1
        assert self.obj.ppmacInstance.numberOfCompTables == 1
        assert self.obj.ppmacInstance.numberOfCamTables == 1
        assert self.obj.ppmacInstance.numberOfECATs == 1
        assert self.obj.ppmacInstance.numberOfEncTables == 1

    def test_sendCommand(self):
        dls_ppmacanalyse.sshClient = Mock()
        attrs = {"sendCommand.return_value": ("0\r0\r0\r\x06", True)}
        dls_ppmacanalyse.sshClient.configure_mock(**attrs)
        assert self.obj.sendCommand("cmd") == ["0", "0", "0"]
        dls_ppmacanalyse.sshClient.sendCommand.assert_called_with("cmd")

    def test_swtblFileToList(self):
        test_file = "/tmp/test.txt"
        with open(test_file, mode="w") as f:
            f.write("test\n\x06")
        ret = self.obj.swtblFileToList(test_file)
        assert ret == [["test"], ["\x06"]]
        os.remove(test_file)

    def test_getDataStructureCategory_1(self):
        ret = self.obj.getDataStructureCategory("test")
        assert ret == "test"

    def test_getDataStructureCategory_2(self):
        ret = self.obj.getDataStructureCategory("other.test[]")
        assert ret == "other"

    def test_ignoreDataStructure_true(self):
        ret = self.obj.ignoreDataStructure("another.test[]", ["another"])
        assert ret is True

    def test_ignoreDataStructure_false(self):
        ret = self.obj.ignoreDataStructure("another.test[]", [])
        assert ret is False

    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "ignoreDataStructure"
    )
    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead"
        ".getDataStructureCategory"
    )
    def test_fillDataStructureIndices_i_ignore_true(
        self, mock_getcategory, mock_ignore
    ):
        data_structure = "test.this[]"
        mock_getcategory.return_value = "test"
        mock_ignore.return_value = True
        self.obj.fillDataStructureIndices_i(data_structure, None, None)
        mock_getcategory.assert_called_with("test.this[]")
        mock_ignore.assert_called_with("test.this[0:]", None)

    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "ignoreDataStructure"
    )
    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "getDataStructureCategory"
    )
    def test_fillDataStructureIndices_i_ignore_false_illegalcmd(
        self, mock_getcategory, mock_ignore
    ):
        dls_ppmacanalyse.sshClient = Mock()
        attrs = {"sendCommand.return_value": ("ILLEGAL\rNone", True)}
        dls_ppmacanalyse.sshClient.configure_mock(**attrs)
        data_structure = "test.this[]"
        mock_getcategory.return_value = "test"
        mock_ignore.return_value = False
        self.obj.fillDataStructureIndices_i(data_structure, None, None)
        mock_getcategory.assert_called_with("test.this[]")
        mock_ignore.assert_called_with("test.this[0]", None)
        dls_ppmacanalyse.sshClient.sendCommand.assert_called_with("test.this[0]")

    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "ignoreDataStructure"
    )
    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead"
        ".getDataStructureCategory"
    )
    def test_fillDataStructureIndices_ij_ignore_true(
        self, mock_getcategory, mock_ignore
    ):
        data_structure = "test.this[]"
        mock_getcategory.return_value = "test"
        mock_ignore.return_value = True
        self.obj.fillDataStructureIndices_ij(data_structure, None, None)
        mock_getcategory.assert_called_with("test.this[]")
        mock_ignore.assert_called_with("test.this[0:]", None)

    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "ignoreDataStructure"
    )
    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "getDataStructureCategory"
    )
    def test_fillDataStructureIndices_ij_ignore_false_illegalcmd(
        self, mock_getcategory, mock_ignore
    ):
        dls_ppmacanalyse.sshClient = Mock()
        attrs = {"sendCommand.return_value": ("ILLEGAL\rNone", True)}
        dls_ppmacanalyse.sshClient.configure_mock(**attrs)
        data_structure = "test.this[]"
        mock_getcategory.return_value = "test"
        mock_ignore.return_value = False
        self.obj.fillDataStructureIndices_ij(data_structure, None, None)
        mock_getcategory.assert_called_with("test.this[]")
        mock_ignore.assert_called_with("test.this[]", None)
        dls_ppmacanalyse.sshClient.sendCommand.assert_called_with("test.this[2]")

    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "ignoreDataStructure"
    )
    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead"
        ".getDataStructureCategory"
    )
    def test_fillDataStructureIndices_ijk_ignore_true(
        self, mock_getcategory, mock_ignore
    ):
        data_structure = "test.this[]"
        mock_getcategory.return_value = "test"
        mock_ignore.return_value = True
        self.obj.fillDataStructureIndices_ijk(data_structure, None, None)
        mock_getcategory.assert_called_with("test.this[]")
        mock_ignore.assert_called_with("test.this[0:]", None)

    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "ignoreDataStructure"
    )
    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "getDataStructureCategory"
    )
    def test_fillDataStructureIndices_ijk_ignore_false_illegalcmd(
        self, mock_getcategory, mock_ignore
    ):
        dls_ppmacanalyse.sshClient = Mock()
        attrs = {"sendCommand.return_value": ("ILLEGAL\rNone", True)}
        dls_ppmacanalyse.sshClient.configure_mock(**attrs)
        data_structure = "test.this[]"
        mock_getcategory.return_value = "test"
        mock_ignore.return_value = False
        self.obj.fillDataStructureIndices_ijk(data_structure, None, None)
        mock_getcategory.assert_called_with("test.this[]")
        mock_ignore.assert_called_with("test.this[]", None)
        dls_ppmacanalyse.sshClient.sendCommand.assert_called_with("test.this[2]")

    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "ignoreDataStructure"
    )
    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead"
        ".getDataStructureCategory"
    )
    def test_fillDataStructureIndices_ijkl_ignore_true(
        self, mock_getcategory, mock_ignore
    ):
        data_structure = "test.this[]"
        mock_getcategory.return_value = "test"
        mock_ignore.return_value = True
        self.obj.fillDataStructureIndices_ijkl(data_structure, None, None)
        mock_getcategory.assert_called_with("test.this[]")
        mock_ignore.assert_called_with("test.this[0:]", None)

    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "ignoreDataStructure"
    )
    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead."
        "getDataStructureCategory"
    )
    def test_fillDataStructureIndices_ijkl_ignore_false_illegalcmd(
        self, mock_getcategory, mock_ignore
    ):
        dls_ppmacanalyse.sshClient = Mock()
        attrs = {"sendCommand.return_value": ("ILLEGAL\rNone", True)}
        dls_ppmacanalyse.sshClient.configure_mock(**attrs)
        data_structure = "test.this[]"
        mock_getcategory.return_value = "test"
        mock_ignore.return_value = False
        self.obj.fillDataStructureIndices_ijkl(data_structure, None, None)
        mock_getcategory.assert_called_with("test.this[]")
        mock_ignore.assert_called_with("test.this[]", None)
        dls_ppmacanalyse.sshClient.sendCommand.assert_called_with("test.this[2]")

    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead.sendCommand")
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead.sendCommand")
    def test_getCoordSystemMotorDefinitions(self, mock_send_coord, mock_send_axes):
        mock_send_coord.return_value = ["1"]
        mock_send_axes.return_value = [
            "&0#0->0",
            "&1#1->i",
            "#2->i",
            "#3->i",
            "#4->i",
            "#5->i",
            "#6->i",
            "&0#7->0",
            "#8->0",
        ]
        coordSystemMotorDefinitions = self.obj.getCoordSystemMotorDefinitions()
        assert coordSystemMotorDefinitions == {
            "0": ["0", ["&0#0->0", "&0#7->0", "&0#8->0"]],
            "1": [
                "1",
                ["&1#1->i", "&1#2->i", "&1#3->i", "&1#4->i", "&1#5->i", "&1#6->i"],
            ],
        }

    # def test_fillDataStructureIndices_ij(self):
    # def test_fillDataStructureIndices_ijk(self):
    # def test_fillDataStructureIndices_ijkl(self):
    # def test_createDataStructuresFromSymbolsTables(self):
    # def test_getActiveElementsFromDataStructures(self):
    # def test_expandSplicedIndices(self):
    # def test_readAndStoreActiveState(self):
    # def test_getBufferedProgramsInfo(self):
    # def test_test_getActiveElementsFromDataStructures


class TestPowerPMAC(unittest.TestCase):
    def setUp(self):
        self.obj = dls_ppmacanalyse.PowerPMAC()

    def test_init(self):
        assert self.obj.source == "unknown"
        assert self.obj.dataStructures == {}
        assert self.obj.activeElements == {}
        assert self.obj.motionPrograms == {}
        assert self.obj.subPrograms == {}
        assert self.obj.plcPrograms == {}
        assert self.obj.forwardPrograms == {}
        assert self.obj.inversePrograms == {}
        assert self.obj.coordSystemDefs == {}


class Stdout:
    def __init__(self, cmdin):
        self.channel = Channel()
        self.cmd = cmdin

    def read(self):
        return self.cmd


class Channel:
    def __init__(self):
        self.exit_status = 0

    def recv_exit_status(self):
        return self.exit_status


class TestPPMACanalyse(unittest.TestCase):
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACanalyse.compare")
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACanalyse.processCompareOptions")
    @patch("logging.basicConfig")
    def setUp(self, mock_log, mock_opts, mock_comp):
        self.ppmacArgs = DummyPpmacArgs()
        self.obj = dls_ppmacanalyse.PPMACanalyse(self.ppmacArgs)

    def test_init(self):
        assert self.obj.resultsDir == "ppmacAnalyse"
        assert self.obj.verbosity == "info"
        assert self.obj.ipAddress == "192.168.56.10"
        assert self.obj.port == 1025
        assert self.obj.operationType == "all"
        assert self.obj.operationTypes == ["all", "active", "project"]
        assert self.obj.backupDir is None
        assert self.obj.username == "root"

    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.fileExists")
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.isValidNetworkInterface")
    def test_processCompareOptions(self, mock_valid, mock_exists):
        mock_valid.return_value = True
        mock_exists.return_value = True
        self.obj.processCompareOptions(self.ppmacArgs)
        assert self.obj.compareSourceA == "test1"
        assert self.obj.compareSourceB == "test2"
        mock_valid.assert_called_with("test2")
        mock_exists.assert_called_with("ignore/ignore")

    # def test_compare(self):
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.fileExists")
    def test_processBackupOptions(self, mock_exists):
        self.ppmacArgs.backup = ["all"]
        mock_exists.return_value = True
        self.obj.processBackupOptions(self.ppmacArgs)

    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.sshClient.connect")
    def test_checkConnection(self, mock_connect):
        mock_connect.return_value = None
        self.obj.checkConnection(False)

    def test_isValidNetworkInterface(self):
        interface = "192.168.56.10:22"
        isValid = dls_ppmacanalyse.isValidNetworkInterface(interface)
        assert isValid is True
        interface = "192.168.56.10:a"
        isValid = dls_ppmacanalyse.isValidNetworkInterface(interface)
        assert isValid is False
        interface = "192.168.b.10:22"
        isValid = dls_ppmacanalyse.isValidNetworkInterface(interface)
        assert isValid is False

    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACCompare.compareActiveElements")
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACCompare.comparePrograms")
    @patch(
        "dls_powerpmacanalyse.dls_ppmacanalyse.PPMACCompare."
        "compareCoordSystemAxesDefinitions"
    )
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACRepositoryWriteRead")
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACHardwareWriteRead")
    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACanalyse.checkConnection")
    def test_compare(
        self,
        mock_connect,
        mock_readwrite,
        mock_repoWriteRead,
        mock_compare1,
        mock_compare2,
        mock_compare3,
    ):
        mock_connect.return_value = True
        self.obj.compareDir = ""
        self.obj.ignoreFile = "/ignore"
        self.obj.compareSourceA = "192.168.10.2:22"
        self.obj.compareSourceB = "/test"
        self.obj.compare()
        mock_readwrite.assert_called_once()
        mock_repoWriteRead.assert_called_once()
        mock_compare1.assert_called_once()
        mock_compare2.assert_called_once()
        mock_compare3.assert_called_once()

    @patch("dls_powerpmacanalyse.dls_ppmacanalyse.sshClient.client.exec_command")
    def test_executeRemoteShellCommand(self, mock_exec):
        mock_exec.return_value = "", Stdout("test cmd"), ""
        dls_ppmacanalyse.executeRemoteShellCommand("cmd")

    def test_nthRepl(self):
        s = "ReplaceNinallplacesNtestN"
        sub = "N"
        repl = "X"
        nth = 2
        res = dls_ppmacanalyse.nthRepl(s, sub, repl, nth)
        assert res == "ReplaceNinallplacesXtestN"

    # @patch("dls_powerpmacanalyse.dls_ppmacanalyse.PPMACanalyse.checkConnection")
    # def test_backup(self, mock_connection):
    #     mock_connection.return_value = True
    #     self.obj.name = "Test"
    #     test_file = "/tmp/test.txt"
    #     self.obj.ignoreFile = test_file
    #     with open(test_file, mode="w") as f:
    #         f.write("Coord[8:]")
    #     self.obj.backup()
    #     os.remove(test_file)
