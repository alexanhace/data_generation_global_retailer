# TODO: Write tests for your package using pytest
def test_with_fixture(faker):
  """Verify that the environment and dependencies are ready."""
  assert isinstance(faker.name(), str)
  assert len(faker.name()) > 0
  
def test_package_import():
  """Verify the local data_generation package is importable."""
  try:
    import data_generation
    assert True
  except ImportError:
    pytest.fail("data_generation package not found in environment")
