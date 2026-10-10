import platform
from pathlib import Path
from src.core.path_utils import get_downloads_path, get_documents_path, get_home_path

def test_get_downloads_path_windows(mocker):
    mocker.patch('platform.system', return_value='Windows')
    mocker.patch.dict('os.environ', {'USERPROFILE': 'C:\\Users\\Test'})
    path = get_downloads_path()
    assert str(path) == 'C:\\Users\\Test\\Downloads'

def test_get_downloads_path_linux(mocker):
    mocker.patch('platform.system', return_value='Linux')
    mocker.patch.object(Path, 'home', return_value=Path('/home/test'))
    path = get_downloads_path()
    assert str(path) == '/home/test/Downloads'

def test_get_documents_path_mac(mocker):
    mocker.patch('platform.system', return_value='Darwin')
    mocker.patch.object(Path, 'home', return_value=Path('/Users/test'))
    path = get_documents_path()
    assert str(path) == '/Users/test/Documents'
