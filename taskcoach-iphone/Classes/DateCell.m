//
//  DateCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 07/06/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "DateCell.h"
#import "DateUtils.h"
#import "i18n.h"


@implementation DateCell

@synthesize dateLabel;

- (void)dealloc
{
	[date release];
	[dateLabel release];
	
	[super dealloc];
}

- (void)setDate:(NSDate *)theDate
{
	[date release];
	date = theDate;

	if (date)
	{
		dateLabel.text = [[TimeUtils instance] stringFromDate:date];
		[switch_ setOn:YES];
	}
	else
	{
		dateLabel.text = _("None");
		[switch_ setOn:NO];
	}
}

@end
