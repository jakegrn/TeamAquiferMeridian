/* mrd_ingest.c - collector daemon front end.
 *
 * Reads a spool file of telemetry frames and appends accepted
 * readings to the store.  Runs from cron on the collector host every
 * fifteen minutes; the "daemon" name is historical.
 *
 * D. Ferreira 2008-04
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "packet.h"
#include "tsstore.h"

#define SPOOL_CHUNK 4096

static void usage(const char *argv0)
{
    fprintf(stderr, "usage: %s <spoolfile> <store.db>\n", argv0);
}

int main(int argc, char **argv)
{
    FILE *f;
    unsigned char buf[SPOOL_CHUNK];
    struct mrd_packet pkt;
    size_t got;
    size_t off;
    long accepted = 0, rejected = 0, suspect = 0;
    int rc;

    if (argc != 3) {
        usage(argv[0]);
        return 1;
    }

    f = fopen(argv[1], "rb");
    if (f == NULL) {
        fprintf(stderr, "mrd_ingest: cannot open spool %s\n", argv[1]);
        return 1;
    }

    if (mrd_store_open(argv[2]) != 0) {
        fprintf(stderr, "mrd_ingest: cannot open store %s\n", argv[2]);
        fclose(f);
        return 1;
    }

    /* Frames are fixed size so the spool is read in whole-frame
     * multiples.  A short tail is discarded with a warning. */
    for (;;) {
        got = fread(buf, 1, SPOOL_CHUNK - (SPOOL_CHUNK % MRD_PACKET_BYTES), f);
        if (got == 0)
            break;

        for (off = 0; off + MRD_PACKET_BYTES <= got; off += MRD_PACKET_BYTES) {
            rc = mrd_packet_parse(buf + off, MRD_PACKET_BYTES, &pkt);
            if (rc != 0) {
                rejected++;
                continue;
            }
            if (pkt.flags & MRD_FLAG_SUSPECT)
                suspect++;
            mrd_store_append(&pkt);
            accepted++;
        }

        if (got % MRD_PACKET_BYTES != 0)
            fprintf(stderr, "mrd_ingest: short tail of %lu bytes discarded\n",
                    (unsigned long)(got % MRD_PACKET_BYTES));
    }

    mrd_store_close();
    fclose(f);

    fprintf(stderr, "mrd_ingest: accepted=%ld rejected=%ld suspect=%ld\n",
            accepted, rejected, suspect);
    return 0;
}
