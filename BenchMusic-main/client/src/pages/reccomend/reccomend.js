import styles from "./recommend.module.css";
import React, { useState, useEffect } from "react";
import axios from "axios";

export default function Recommend() {
  const [user, setUser] = useState(null);
  const [spotifyLoggedIn, setSpotifyLoggedIn] = useState(false);
  const [playlists, setPlaylists] = useState([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

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

  const handlePlaylistChange = (event) => {
    setSelectedPlaylist(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (selectedPlaylist) {
      console.log("Selected playlist:", selectedPlaylist);
      axios
        .post("https://localhost:5000/get-recommendations", {
          playlist_id: selectedPlaylist,
        })
        .then((response) => {
          setRecommendations(response.data.recommendations);
        })
        .catch((error) => {
          console.error("Error fetching recommendations:", error);
        });
    } else {
      alert("Please select a playlist.");
    }
  };

  return (
    <div className={styles.reccomend}>
      <h1 className={styles.homeHeader}>
        Get recommendations based on your playlist.
      </h1>
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
          <form className={styles.playSel} onSubmit={handleSubmit}>
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
          <br />
            <button
              type="submit"
              className={`${styles.linkBtn} ${styles.transYTBtn}`}
            >
              Get Recommendations
            </button>
          </form>
        </div>
        <div className={styles.playlistForm}>
          <h3 className={styles.recommendationsHeader}>Recommendations:</h3>
          <ul className={styles.recommendationsList}>
            {recommendations.map((recommendation, index) => (
              <li key={index} className={styles.recommendationItem}>
                {recommendation}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
