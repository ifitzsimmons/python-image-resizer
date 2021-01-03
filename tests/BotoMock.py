from unittest.mock import  MagicMock
class BotoMock:
  def client(self):
    return MagicMock()