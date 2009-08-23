//
//  DateCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 07/06/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "DateCell.h"
#import "i18n.h"


@implementation DateCell

@synthesize dateLabel;

- (void)dealloc
{
	[dateLabel release];
	
	[super dealloc];
}

- (void)setDate:(NSString *)date
{
	if (date)
	{
		dateLabel.text = date;
		[switch_ setOn:YES];
	}
	else
	{
		dateLabel.text = _("None");
		[switch_ setOn:NO];
	}
}

@end
