export interface Drawing {
  image: string;
  title?: string;
  note?: string;
}

export const drawings: Drawing[] = [
  {
    image: "/drawings/portrait-sketch.jpg",
    title: "Portrait Study",
    note: "Pencil-style line study — loose hair strokes and light cross-hatching on warm paper.",
  },
  {
    image: "/drawings/architectural-study.jpg",
    title: "Architectural Study",
    note: "Ink sketch of arches, pillars and a rooftop silhouette against a hatched sky.",
  },
];
