//
//  TaskDetailsViewiPad.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 04/07/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskDetailsViewiPad.h"


@implementation TaskDetailsViewiPad

- initWithCoder:(NSCoder *)coder
{
	if ((self = [super initWithCoder:coder]))
		bgImage = [[UIImage imageNamed:@"paper_big.png"] retain];

	return self;
}

- (void)dealloc
{
	[bgImage release];

	[super dealloc];
}

#pragma mark Drawing

- (void)drawRect:(CGRect)rect
{
	CGContextRef context = UIGraphicsGetCurrentContext();
	CGContextSaveGState(context);
	CGContextClipToRect(context, rect);
	CGContextDrawTiledImage(context, CGRectMake(0, 0, 40, 40), bgImage.CGImage);
	CGContextRestoreGState(context);

	[super drawRect:rect];
}

@end
