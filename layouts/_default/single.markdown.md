# {{ .Title }}

*{{ .Date.Format "2006-01-02" }}*{{ with .Params.tags }} | tags: {{ delimit . ", " }}{{ end }}

Source: {{ .Permalink }}

---

{{ .RawContent }}
