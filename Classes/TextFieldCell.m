//
//  TextFieldCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TextFieldCell.h"

@implementation TextFieldCell

@synthesize textField;

- (void)dealloc
{
	[textField release];

    [super dealloc];
}

@end
