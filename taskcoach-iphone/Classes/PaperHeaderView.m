//
//  PaperHeaderView.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 27/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "PaperHeaderView.h"

@implementation PaperHeaderView

@synthesize label;

- initWithCoder:(NSCoder *)coder
{
	if ((self = [super initWithCoder:coder]))
		bgImage = [UIImage imageNamed:@"headerbg.png"];

	return self;
}

- (void)dealloc
{
	[bgImage release];

	self.label = nil;

    [super dealloc];
}

@end
