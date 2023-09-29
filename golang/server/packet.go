package cloudlink

// This structure represents the JSON formatting used for the current CloudLink formatting scheme.
// Values that are not specific to one type are represented with interface{}.
type PacketUPL struct {
	Cmd      string      `json:"cmd"`
	Name     interface{} `json:"name,omitempty"`
	Val      interface{} `json:"val,omitempty"`
	ID       interface{} `json:"id,omitempty"`
	Rooms    interface{} `json:"rooms,omitempty"`
	Listener interface{} `json:"listener,omitempty"`
	Code     string      `json:"code,omitempty"`
	CodeID   int         `json:"code_id,omitempty"`
	Mode     string      `json:"mode,omitempty"`
	Origin   *UserObject `json:"origin,omitempty"`
	Details  string      `json:"details,omitempty"`
}

// This structure represents the JSON formatting the Scratch cloud variable protocol uses.
// Values that are not specific to one type are represented with interface{}.
type Scratch struct {
	Method    string      `json:"method"`
	ProjectID interface{} `json:"project_id,omitempty"`
	Username  string      `json:"user,omitempty"`
	Value     interface{} `json:"value"`
	Name      interface{} `json:"name,omitempty"`
	NewName   interface{} `json:"new_name,omitempty"`
}
