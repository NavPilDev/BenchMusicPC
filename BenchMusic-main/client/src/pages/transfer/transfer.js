import React, { useState, useEffect } from "react";
import axios from "axios";

import styles from "./transfer.module.css";

function Transfer() {
  const [user, setUser] = useState(null);
  const [user2, setUser2] = useState(null);
  const [spotifyLoggedIn, setSpotifyLoggedIn] = useState(false);
  const [youtubeLoggedIn, setYoutubeLoggedIn] = useState(false);
  const [playlists, setPlaylists] = useState([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState(null);
  const [text, setText] = useState(["Transfer Playlist to YouTube"]);

  useEffect(() => {
    // Fetch user's information and playlists from backend after successful login
    axios
      .get("https://localhost:5000/user-info")
      .then((response) => {
        setUser(response.data.username);
        if (response.data.username) {
          setSpotifyLoggedIn(true);
        }
      })
      .catch((error) => {
        console.error("Error fetching user info:", error);
      });

    //Fetch user's information from YouTube
    axios
      .get("https://localhost:5000/youtube-user-info")
      .then((response) => {
        setUser2(response.data.youtubeusername);
        if (response.data.youtubeusername) {
          // Ensure username is not null or "null" string
          setYoutubeLoggedIn(true);
        }
      })
      .catch((error) => {
        console.error("Error fetching YouTube user info:", error);
      });

    // Fetch Spotify playlists
    axios
      .get("https://localhost:5000/playlists")
      .then((response) => {
        setPlaylists(response.data.playlists.items);
      })
      .catch((error) => {
        console.error("Error fetching playlists:", error);
      });
  }, []);

  const handleSpotifyLogin = () => {
    window.location.href = "https://localhost:5000/login"; // Redirect to Spotify login route
  };

  const handleYoutubeLogin = () => {
    window.location.href = "https://localhost:5000/authorize-youtube"; // Redirect to YouTube login route
  };

  const handlePlaylistChange = (event) => {
    setSelectedPlaylist(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (selectedPlaylist) {
      console.log("Selected playlist:", selectedPlaylist);
      // Send selected playlist to backend for further processing
    } else {
      alert("Please select a playlist.");
    }
  };

  const handleTransferPlaylist = () => {
    axios
      .post(
        "https://localhost:5000/transfer-playlist",
        {
          playlist_id: selectedPlaylist,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      )
      .then((response) => {
        console.log("Playlist transferred successfully:", response.data);
        setText("Complete! ✅");
      })
      .catch((error) => {
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          console.error(
            "Server responded with error status:",
            error.response.status
          );
          console.error(
            "Server responded with error data:",
            error.response.data
          );
        } else if (error.request) {
          // The request was made but no response was received
          console.error("No response received from server:", error.request);
        } else {
          // Something happened in setting up the request that triggered an Error
          console.error("Error setting up request:", error.message);
        }
      });
  };

  return (
    <div id="transfer" className={styles.transfer}>
      <div className={styles.formLinks}>
        <div className={styles.loginLinks}>
          {spotifyLoggedIn && <p>Hello, {user}!</p>}
          {!spotifyLoggedIn && (
            <button
              onClick={handleSpotifyLogin}
              className={`${styles.linkBtn} ${styles.spotifyBtn}`}
            >
              Login with Spotify
            </button>
          )}
          <br />

          {youtubeLoggedIn && <p>Connected to: {user2}</p>}
          {!youtubeLoggedIn && (
            <button
              onClick={handleYoutubeLogin}
              className={`${styles.linkBtn} ${styles.youtubeBtn}`}
            >
              Login with YouTube
            </button>
          )}
          {/* <br /> */}
        </div>
        <div className={styles.playlistForm}>
          <form className={styles.playSel} onSubmit={handleSubmit}>
            {/* <label htmlFor="playlist-select">Choose a playlist:</label> */}
            <select
              className={styles.playlistSelect}
              name="playlist-select"
              onChange={handlePlaylistChange}
            >
              <option value="" disabled selected>
                Select Playlist
              </option>
              {playlists.map((playlist) => (
                <option key={playlist.id} value={playlist.id}>
                  {playlist.name}
                </option>
              ))}
            </select>
          </form>
          <br />
          <button
            onClick={handleTransferPlaylist}
            className={`${styles.linkBtn} ${styles.transYTBtn}`} 
            >{text}
            
          </button>
        </div>
      </div>
    </div>
  );
}

export default Transfer;