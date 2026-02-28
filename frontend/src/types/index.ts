export interface Movie {
  id: number;
  title: string;
  description: string;
  year: number;
  duration: number;
  genre: string;
  poster: string | null;
  created_at: string;
}

export interface Session {
  id: number;
  movie: number;
  movie_title: string;
  date: string;
  hall_number: number;
}

export interface Review {
  id: number;
  movie: number;
  username: string;
  text: string;
  rating: number;
  created_at: string;
}
