import styles from "./home.module.css";
import { Link, useResolvedPath, useMatch } from "react-router-dom";

function CustomLink({ to, children, ...props }) {
  const resolvedPath = useResolvedPath(to);
  const isActive = useMatch({ path: resolvedPath.pathname, end: true });

  return (
    <button className={isActive ? "active" : ""}>
      <Link to={to} {...props}>
        {children}
      </Link>
    </button>
  );
}

export default function Home() {
  return (
    <main className={styles.home}>
      <h1 className={styles.homeHeader}>
        Convert your Spotify playlist and listen on YouTube.
      </h1>
      <CustomLink className={styles.homeBtn} to="/transfer">
        Get Started
      </CustomLink>
    </main>
  );
}