#!/bin/bash
INPUT_DIR="/mnt/c/Users/moham/Desktop/thesis/thesis-data/captures/pcap-captures/catwatch"
OUTPUT_DIR="/mnt/c/Users/moham/Desktop/thesis/thesis-data/captures/csv-captures/catwatch"
mkdir -p "$OUTPUT_DIR"
echo "starting"
for pcap_file in "$INPUT_DIR"/*.pcap*; do
    if [[ -f "$pcap_file" ]]; then
        echo $pcap_file
        output_file="$OUTPUT_DIR/$(basename "${pcap_file%.pcap}").csv"
        
        tshark -r "$pcap_file" -Y http.request -T fields \
            -e http.request.method \
            -e http.request.full_uri \
            -e http.user_agent \
            -e http.accept \
            -e http.authorization \
            -e http.file_data \
            -E header=y -E separator='|' -E occurrence=f > "$output_file"
        
        echo "Processed: $pcap_file -> $output_file"
    fi
done

echo "Processing complete."
