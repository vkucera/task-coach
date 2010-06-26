    //
//  SimpleDatePicker.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "SimpleDatePicker.h"
#import "i18n.h"

@implementation SimpleDatePicker

@synthesize picker;
@synthesize okButton;

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

- (void)viewWillAppear:(BOOL)animated
{
	if (date)
		[picker setDate:date animated:NO];
	[okButton setTitle:_("OK") forState:UIControlStateNormal];

	[super viewWillAppear:animated];
}

- (void)viewDidUnload
{
    [super viewDidUnload];

	self.picker = nil;
	self.okButton = nil;
}

- (void)dealloc
{
	[self viewDidUnload];
	
	[date release];

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

- (void)setDate:(NSDate *)aDate
{
	[date release];
	date = [aDate retain];
}

@end
