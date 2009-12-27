//
//  ButtonCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 27/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import "ButtonCell.h"


@implementation ButtonCell

@synthesize button;

- (void)setTarget:(id)theTarget action:(SEL)theAction
{
	target = theTarget;
	action = theAction;
}

- (IBAction)onClicked:(UIButton *)btn
{
	[target performSelector:action withObject:self];
}

- (void)dealloc
{
	self.button = nil;

    [super dealloc];
}

@end
