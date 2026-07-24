{{- define "soundops.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "soundops.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "soundops.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "soundops.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "soundops.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "soundops.selectorLabels" -}}
app.kubernetes.io/name: {{ include "soundops.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
