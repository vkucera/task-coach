    //
//  SimpleDatePicker.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "SimpleDatePicker.h"

@implementation SimpleDatePicker

@synthesize picker;

- initWithTarget:(id)theTarget action:(SEL)theAction
{
	if (self = [super initWithNibName:@"SimpleDatePicker" bundle:[NSBundle mainBundle]])
	{
		target = theTarget;
		action = theAction;
	}

	return self;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

- (void)viewDidUnload
{
    [super viewDidUnload];

	self.picker = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

    [super dealloc];
}

- (IBAction)onClickNone:(UIButton *)button
{
	[target performSelector:action];
}

- (NSDate *)date
{
	return picker.date;
}

- (void)setDate:(NSDate *)date
{
	if (date)
	{
		picker.date = date;
	}
}

@end
