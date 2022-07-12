from videoanalyzer.source.rtspsource import RtspSource

def test_rtspsource_get_url():
    url = "rtsp://localhost:5555"
    source = RtspSource(url)
    assert source.url == url