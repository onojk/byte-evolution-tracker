# byte-evolution-tracker

Reverse engineering notes for the **Lenovo ThinkPad T430u** firmware — BIOS, Intel Management Engine region, and Embedded Controller.

This repository started life as a hex-byte experiment (now in [`archive/`](archive/)) and has been repurposed for the analysis it was always reaching toward: actually understanding what's in this hardware.

## Status

Work in progress. Slow, hobbyist pace. One Lenovo UEFI module fully decoded so far.

## What's here

```
t430u/
├── dumps/         vendor firmware (gitignored — never committed)
├── extracted/     UEFITool output (gitignored)
│   └── modules/   .efi modules pulled from the BIOS volume
├── notes/         markdown analysis notes — the actual findings
├── scripts/       small helpers (e.g. extract_module.sh)
└── ghidra-projects/  Ghidra working data (gitignored)

archive/           the original byte-evolution-tracker, kept for history
```

The vendor firmware itself is not in git, by design. Only notes, scripts, and analysis.

## Hardware

- **Model**: ThinkPad T430u (Quanta-built ultrabook variant, Ivy Bridge generation)
- **BIOS**: Phoenix-based UEFI, build `H665a 11/09/12`
- **ME firmware**: Intel ME 8.1.3.1325 (Ivy Bridge era)
- **EC**: ITE 8528-class embedded controller

Three SPI dumps are the source material:
- 4 MB BIOS region
- 8 MB descriptor + ME region
- 512 KB EC firmware

These are sitting in `t430u/dumps/` locally on the analyst's machine; they are not part of the repository.

## Findings so far

### `LenovoWmaPolicyDxe.efi` — Wireless Whitelist

See [`t430u/notes/wireless_whitelist.md`](t430u/notes/wireless_whitelist.md).

The full 30-entry hardware whitelist has been decoded. Each entry is 12 bytes and identifies an approved wireless card (PCI Mini-PCIe or USB-attached Bluetooth/WWAN). The comparison function `FUN_00000ae0` has been mapped, and the spots in the code that decide "approved / unauthorized 1802 error" are documented.

This is the mechanism behind the famous `1802: Unauthorized network card is plugged in` boot error. The notes document how it works — they do not provide a patched BIOS.

## What to look out for going forward

A non-exhaustive map of where this is heading. Anyone reading along (or future me) — these are the threads to follow:

- **`FUN_00000fa8`** — the callback registered by `LenovoWmaPolicyDxe`. This is what fires on hardware enumeration and produces the actual 1802 error message. Hasn't been read yet.
- **`LenovoSvpManagerDxe.efi`** — supervisor password handling. Already extracted, not yet analyzed. Sensitive territory; documenting how the password check works does not unlock anyone's hardware, but the code is interesting.
- **`LenovoPasswordCp.efi`** — small companion password module, also extracted.
- **`AbsoluteComputraceInstallerWin8.efi`** — the LoJack/Computrace persistence module that's known to live in the BIOS. Worth understanding how Lenovo wired it in.
- **`QuantaSetupAutomationSmm.efi`** — Quanta-specific (this was a Quanta-built T430u, not Wistron like the regular T430). SMM modules are where the most privileged code in the system runs. Read carefully.
- **The 8 MB ME region** — Intel ME 8.1 is the era exploitable by `deguard` (CVE-2017-5705). Worth understanding the partition layout and `$FPT` table even if no actual ME modification is performed here.
- **The EC dump** — ITE 8528 firmware. Different processor, will need a different Ghidra processor module. Long-term project.
- **Cross-referencing with Coreboot** — the T430 (Wistron) is supported by Coreboot/Heads. The T430u (Quanta) is not. Understanding the differences could eventually contribute upstream.

## Tools used

- [Ghidra](https://ghidra-sre.org/) 12.0.4 — disassembly and decompilation
- [UEFITool](https://github.com/LongSoft/UEFITool) — BIOS volume parsing and module extraction
- [binwalk](https://github.com/ReFirmLabs/binwalk) — initial recon
- Python 3 — small parsing scripts

## Why this exists

A T430u was the author's machine for a long time. It's a sentimental piece of hardware and one of the more interesting ThinkPads — the only Ivy Bridge ultrabook in the line, built by a different ODM than the rest of the T-series. Understanding it deeply is the point. There is no fork, no patched BIOS, no release artifact. Just notes.

## License & ethics

- Notes and scripts in this repository: MIT.
- Vendor firmware: not redistributed. The dumps remain on the analyst's local machine. Anything in this repo is independent analysis written from observation.
- Nothing in this repository is a tool for bypassing security on a machine the reader does not own.
