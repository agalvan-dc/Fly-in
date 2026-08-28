# Fly-in

  r"""
        Regex pattern: r"(-?\d+)\s+(-?\d+)\s*\[" (matches up to '[')

        Extracts integer (X, Y) coordinates appearing right before an options block '[...]'.

        Breakdown:
            - (-?\d+)  : Captures group 1 (X) & group 2 (Y); matches optional '-' sign and 1+ digits.
            - \s+      : Requires 1+ whitespace characters between the coordinates.
            - \s*\[    : Matches optional spaces followed by a literal opening bracket.
        
        Example: "junction -1 0 [color=yellow]" -> Group 1: "-1", Group 2: "0"
        """
 """
        Extracts key-value pairs from an options block '[key=value ...]'.

        Breakdown:
            - re.findall : Captures the string inside the brackets '[]'.
            - split()    : Divides the captured string by spaces to isolate pairs.
            - split('=') : Separates keys and values. Attempts to cast numeric values to integers.

        Example: "[color=yellow max_drones=2]" -> {'color': 'yellow', 'max_drones': 2}
        """

