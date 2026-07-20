# {{ .Params.name }}
**{{ .Params.tagline }}**{{ with .Params.work_permit }} | Work permit: {{ . }}{{ end }}

{{ with .Params.website }}- Website: {{ . }}
{{ end }}{{ with .Params.linkedin_url }}- LinkedIn: {{ . }}
{{ end }}{{ with .Params.github_url }}- GitHub: {{ . }}
{{ end }}{{ with .Params.blog }}- Blog: {{ .url }}{{ with .note }} ({{ . }}){{ end }}
{{ end }}
Source: {{ .Permalink }}

---

## About

{{ .Params.about | strings.TrimSpace }}

---

## Skills
{{ range .Params.skills }}
### {{ .category }}
{{ delimit .items ", " }}
{{ end }}
---

## Experience
{{ range .Params.experience }}
### {{ .title }} — {{ .company }}
**{{ .period }}**{{ with .location }} | {{ . }}{{ end }}

{{ .description | strings.TrimSpace }}
{{ with .bullets }}
{{ range . }}- {{ . }}
{{ end }}{{ end }}
{{ end }}
---

## Projects
{{ range .Params.projects }}
### {{ .name }}
{{ .description | strings.TrimSpace }}
{{ with .link }}Link: {{ . }}
{{ end }}
{{ end }}
---

## Education
{{ range .Params.education }}
### {{ .degree }}
{{ .institution }}{{ with .location }} | {{ . }}{{ end }}{{ with .period }} | {{ . }}{{ end }}{{ with .grade }} | Grade: {{ . }}{{ end }}
{{ with .website }}{{ . }}{{ end }}
{{ end }}
---

## Languages
{{ range .Params.languages }}- {{ .language }}: {{ .level }}{{ with .note }} — {{ . }}{{ end }}
{{ end }}
---

## Driving Licence
{{ .Params.driving_licence }}
