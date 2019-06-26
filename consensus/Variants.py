class Variants:
    @staticmethod
    def need_simplification(ref, alt):
        return len(ref) > 0 and len(alt) > 0 and ref[0] == alt[0]

    @staticmethod
    def get_variant_type(raw_ref, raw_alt):
        ref, alt = Variants._simplify_ref_alt(raw_ref, raw_alt)

        if ref == '.':
            variant_type = 'ins'
        elif alt == '.':
            variant_type = 'del'
        elif len(ref) == 1 and len(alt) == 1:
            variant_type = 'snp'
        else:
            variant_type = 'delins'

        return variant_type

    @staticmethod
    def _strip_matching_seq_start(ref, alt):
        """
        This functions strips the matching starts of the ref and alt (for instance: CTGGTG>CTGGCG becomes TG>CG)
        :param ref: the reference sequence
        :param alt: the alternative sequence
        :return: the ref and alt without their matching start
        """
        while Variants.need_simplification(ref, alt):
            ref = ref[1::]
            alt = alt[1::]
        return ref, alt

    @staticmethod
    def _get_actual_ref_and_alt(ref, alt):
        """
        This functions strips the matching start and stops of the ref and alt (for instance: CTGGTG>CTGGCG becomes T>C)
        :param ref: the reference sequence
        :param alt: the alternative sequence
        :return: the ref and alt without their matching start and stop
        """
        # Check if the first character is the same
        if ref[0] == alt[0]:
            # Remove the matching start
            ref, alt = Variants._strip_matching_seq_start(ref, alt)

        # Check if the last character is the same
        if len(ref) > 0 and len(alt) > 0 and ref[-1] == alt[-1]:
            # Pass the reversed sequence to the strip start to remove the matching start of it (== end of the sequence)
            r_ref, r_alt = Variants._strip_matching_seq_start(ref[::-1], alt[::-1])
            # Turn the sequences around again
            ref = r_ref[::-1]
            alt = r_alt[::-1]

        return ref, alt

    @staticmethod
    def _simplify_ref_alt(raw_ref, raw_alt):
        """
        Writes the ref and alt as short as possible (duplicate ending and beginning are removed, and if none left
        replaced by .)
        :param raw_ref: the potentially long ref
        :param raw_alt: the potentially long alt
        :return: tuple with short ref and alt
        """
        # If ref and alt are same length, stripping function won't work
        # Skip ref/alt for which length == 1, for performance
        ref, alt = Variants._get_actual_ref_and_alt(raw_ref, raw_alt)
        if len(ref) == 0:
            ref = '.'
        elif len(alt) == 0:
            alt = '.'
        return ref, alt
