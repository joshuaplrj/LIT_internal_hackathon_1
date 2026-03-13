# CYBER-2: Rootkit Genesis — Building and Detecting Kernel-Level Persistence

## Overview

*Note: This is a controlled lab exercise. All work must be done on the provided isolated VM.*

Design a **kernel-level rootkit** for Linux and then detect rootkits planted by other teams.

## Part A — Offense (40%)

Build a kernel-level rootkit that:

1. **Process Hiding**: Hide specific processes from `ps`, `top`, `/proc`
2. **File Hiding**: Intercept filesystem read operations to hide files
3. **Reverse Shell**: Reconnect every 60 seconds if disconnected
4. **Persistence**: Survive reboot via init script or bootloader hook
5. **Anti-Forensics**: At least 2 techniques (log deletion, timestomping, memory-only execution)

## Part B — Defense (60%)

Analyze a compromised VM (without knowing your own rootkit's specifics):

1. Detect all hidden processes and files
2. Identify persistence mechanism
3. Trace network callback to C2 destination
4. Extract rootkit configuration
5. Produce compromise timeline

## Technical Requirements

### Kernel Module Basics

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

static int __init rootkit_init(void) {
    printk(KERN_INFO "Rootkit loaded\n");
    return 0;
}

static void __exit rootkit_exit(void) {
    printk(KERN_INFO "Rootkit unloaded\n");
}

module_init(rootkit_init);
module_exit(rootkit_exit);
MODULE_LICENSE("GPL");
```

### Syscall Hooking

```c
// Hook syscall table to intercept calls
unsigned long *syscall_table;

// Original syscall pointer
asmlinkage long (*original_read)(int fd, char __user *buf, size_t count);

// Hooked syscall
asmlinkage long hooked_read(int fd, char __user *buf, size_t count) {
    // Call original
    long ret = original_read(fd, buf, count);
    
    // Filter/hide data
    if (should_hide(fd)) {
        return filter_output(buf, ret);
    }
    
    return ret;
}
```

### Process Hiding Techniques

1. **Hook `getdents`/`getdents64`**: Filter directory entries
2. **Hook `/proc` read**: Hide process directories
3. **Unlink from task list**: Remove from kernel task list

### Persistence Mechanisms

1. **Init script**: `/etc/init.d/` or systemd service
2. **Cron job**: `@reboot` entry
3. **LD_PRELOAD**: Library injection
4. **Kernel module auto-load**: `/etc/modules-load.d/`
5. **Bootloader hook**: initramfs modification

### Anti-Forensics Techniques

1. **Log deletion**: Remove entries from `/var/log/`
2. **Timestomping**: Modify file timestamps
3. **Memory-only execution**: Execute from `/dev/shm` or tmpfs
4. **Log level manipulation**: Suppress kernel messages
5. **Process name spoofing**: Masquerade as legitimate process

## Detection Tools

### Memory Forensics (Volatility)

```bash
# List processes
volatility -f memory.dump --profile=LinuxProfile linux_pslist

# Compare with hidden processes
volatility -f memory.dump --profile=LinuxProfile linux_psaux

# Check for hidden modules
volatility -f memory.dump --profile=LinuxProfile linux_lsmod

# Check syscall table
volatility -f memory.dump --profile=LinuxProfile linux_check_syscall
```

### Disk Forensics

```bash
# Find recently modified files
find / -mtime -7 -type f 2>/dev/null

# Check for suspicious kernel modules
lsmod | grep -v "^Module" | while read mod size used; do
    modinfo $mod 2>/dev/null | grep -q "signature" || echo "Unsigned: $mod"
done

# Check init scripts
ls -la /etc/init.d/ /etc/systemd/system/ /etc/rc*.d/
```

### Network Analysis

```bash
# Check connections
ss -tunap
netstat -tunap

# Monitor DNS
tcpdump -i any port 53

# Check for beaconing
tshark -r capture.pcap -Y "tcp.flags.syn==1" -T fields -e ip.dst | sort | uniq -c | sort -rn
```

## Deliverables

### Part A
- Source code (kernel module + userspace components)
- Build instructions (Makefile)
- Deployment script
- Documentation of techniques used

### Part B
- Forensic report (PDF)
- Detection scripts
- IOCs (Indicators of Compromise)
- Timeline of compromise

## Scoring

| Criterion | Points |
|---|---|
| Offense: Stealth (undetected duration) | 15 |
| Offense: Feature completeness | 15 |
| Offense: Code quality | 10 |
| Defense: Detection completeness | 25 |
| Defense: Timeline accuracy | 20 |
| Defense: IOC quality | 15 |

## Project Structure

```
CYBER-2_RootkitGenesis/
├── README.md
├── offense/
│   ├── src/
│   │   ├── rootkit.c
│   │   ├── hooks.c
│   │   ├── hide.c
│   │   ├── persistence.c
│   │   └── anti_forensics.c
│   ├── Makefile
│   ├── deploy.sh
│   └── config.json
├── defense/
│   ├── detect_processes.sh
│   ├── detect_files.sh
│   ├── detect_network.sh
│   ├── memory_analysis.py
│   └── report_template.md
├── tools/
│   ├── volatility_plugins/
│   └── scripts/
└── solution_template.py
```

## Warning

⚠️ This exercise is for **educational purposes only** in a controlled lab environment. Creating or deploying rootkits on systems without authorization is illegal and unethical.
