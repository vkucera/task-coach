//
//  SwitchCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "SwitchCell.h"

@implementation SwitchCell

@synthesize label;
@synthesize switch_;

- (IBAction)onValueChanged:(UISwitch *)s
{
	[delegate onSwitchValueChanged:self];
}

- (void)setDelegate:(id <SwitchCellDelegate>)deleg
{
	delegate = deleg;
}

@end
