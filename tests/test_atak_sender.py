from unittest.mock import MagicMock, patch

from signal_atak_bot.atak_sender import send_cot


@patch("signal_atak_bot.atak_sender.socket.socket")
def test_send_unicast(mock_socket_class):
    mock_sock = MagicMock()
    mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
    mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

    send_cot("<event/>", "192.168.1.100", 4242, multicast=False)

    mock_sock.sendto.assert_called_once()
    args = mock_sock.sendto.call_args
    assert args[0][0] == b"<event/>"
    assert args[0][1] == ("192.168.1.100", 4242)
    mock_sock.setsockopt.assert_not_called()


@patch("signal_atak_bot.atak_sender.socket.socket")
def test_send_multicast(mock_socket_class):
    mock_sock = MagicMock()
    mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
    mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

    send_cot("<event/>", "239.2.3.1", 6969, multicast=True)

    mock_sock.setsockopt.assert_called_once()
    mock_sock.sendto.assert_called_once()
    args = mock_sock.sendto.call_args
    assert args[0][1] == ("239.2.3.1", 6969)
