//
//  DateCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 07/06/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "DateCell.h"


@implementation DateCell

@synthesize dateLabel;

- (void)setDate:(NSString *)date
{
	if (date)
	{
		dateLabel.text = date;
		[switch_ setOn:YES];
	}
	else
	{
		dateLabel.text = NSLocalizedString(@"None", @"No date set label");
		[switch_ setOn:NO];
	}
}

@end
