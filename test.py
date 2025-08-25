from ecmwf_client import download_forecast

def test_download_forecast(monkeypatch):
    class DummyClient:
        def retrieve(self, **kwargs):
            assert "target" in kwargs
    monkeypatch.setattr("ecmwf_client.Client", lambda source: DummyClient())
    download_forecast("test.grib")