# Sailfish debug evidence

These files document the Sailfish OS port only. Earlier records can describe failed experiments or superseded states; current results are in the repository README and `release/BUILD-STATUS.json`.

Network identifiers, credentials, raw framebuffer buffers, device backups, user data and keys are excluded. The phone clock was unset and reports 2014-05-20 in many logs; host capture names and monotonic times establish sequence.

Post-alpha3 evidence covers Gallery pinch stability, camera startup, QDSP speaker gain and power-key handling. Alpha4 revision 3 packaging evidence is in `sailfish-alpha4-patch-manifest.json`, `sailfish-alpha4-verification.json`, `sailfish-alpha4-package-verification.json` and `sailfish-alpha4-r3-zip-test.log`. The clean image passed 67 critical-file read-backs and filesystem/ZIP checks; it has not had a separate clean-image cold boot.
