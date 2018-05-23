# (c) 2018 Dean Stamler

from datetime import datetime
import logging

def snap_to_bound(raw_date_string, bound, upper=False):
    log = logging.getLogger()

    # Generate both posible datetime objects from raw_date_string
    # Check to ensure the resulting datetime objects are greater than the
    # lower_bound (default) or less than the upper_bound and discard
    # (set value to None) one or both if they don't meet thid criteria
    dmy = datetime.strptime(raw_date_string,'%d/%m/%Y %I:%M:%S %p')
    mdy = datetime.strptime(raw_date_string,'%m/%d/%Y %I:%M:%S %p')

    if (upper):
        bdisp = 'upper'
    else:
        bdisp = 'lower'

    log.debug("      snapping %s to %s bound %s", raw_date_string, bdisp, bound)
    log.debug("        Choices: %s and %s", dmy, mdy)
    if(upper):
        if (dmy > bound):
            dmy = None
        if (mdy > bound):
            mdy = None
    else:
        if (dmy < bound):
            dmy = None
        if (mdy < bound):
            mdy = None

    if (dmy):
        if (mdy):
            # both are defined so find the closest one
            if(abs(dmy - bound) < abs(mdy - bound)):
                log.debug("        Chose %s", dmy)
                return dmy
            else:
                log.debug("        Chose %s", mdy)
                return mdy

        else:
            log.debug("        Chose %s", dmy)
            return dmy
    elif (mdy):
        log.debug("        Chose %s", mdy)
        return mdy
    else:
        # Both choices are out of bounds (None), raise an exception
        raise ValueError("Both interpretations of {} are {} than {}".format(
            raw_date_string, 'greater' if upper else 'less', bound
            ))

def infer(lower_bound, upper_bound, string_list, descending=False):
    log = logging.getLogger()
    if(lower_bound):
        lb = lower_bound
    else:
        lb='no lower bound'
    if(upper_bound):
        ub = upper_bound
    else:
        ub='no upper bound'
    log.debug('    infer called with bounds of %s and %s', lb, ub)
    out_list = [] # a list of datetime objects

    if(descending):
        if(upper_bound):
            for raw_date_string in string_list:
                upper_bound = snap_to_bound(raw_date_string, upper_bound, True)
                out_list.append(upper_bound)
            return out_list
        elif(lower_bound):
            for raw_date_string in reversed(string_list):
                lower_bound = snap_to_bound(raw_date_string, lower_bound)
                out_list.append(lower_bound)
            out_list.reverse()
            return out_list
        else:
            raise ValueError('infer() was called with no bounds arguments')

    else:
        if(lower_bound):
            for raw_date_string in string_list:
                lower_bound = snap_to_bound(raw_date_string,lower_bound)
                out_list.append(lower_bound)
            return out_list
        elif(upper_bound):
            for raw_date_string in reversed(string_list):
                upper_bound = snap_to_bound(raw_date_string,upper_bound,True)
                out_list.append(upper_bound)
            out_list.reverse()
            return out_list
        else:
            raise ValueError('infer() was called with no bounds arguments')
