//
//  BadgedCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/10/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "BadgedCell.h"

@implementation BadgedCell

@synthesize badge;
@synthesize textLabel;

- initWithCoder:(NSCoder *)coder
{
	if ((self = [super initWithCoder:coder]))
	{
		if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
			bgImage = [[UIImage imageNamed:@"leather.png"] retain];
	}

	return self;
}

- (void)dealloc
{
	[bgImage release];
	self.badge = nil;
	self.textLabel = nil;

	[super dealloc];
}

- (CGSize)sizeThatFits:(CGSize)size
{
	return size;
}

- (void)layoutSubviews
{
	[self.badge sizeToFit];

	[super layoutSubviews];
}

- (void)willTransitionToState:(UITableViewCellStateMask)state
{
	self.badge.hidden = ((state & UITableViewCellStateEditingMask) != 0);

	[super willTransitionToState:state];

}

- (void)didTransitionToState:(UITableViewCellStateMask)state
{
	[super didTransitionToState:state];
	[self setNeedsDisplay];
}

- (void)drawRect:(CGRect)rect
{
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		CGContextRef context = UIGraphicsGetCurrentContext();
		CGContextSaveGState(context);

		CGContextDrawTiledImage(context, CGRectMake(0, 0, 64, 64), bgImage.CGImage);

		CGContextSetRGBStrokeColor(context, 0, 0, 0, 1);
		CGContextSetRGBFillColor(context, 1, 1, 1, 1);

		CGFloat x, y, w, h;
		x = self.textLabel.frame.origin.x;
		y = self.textLabel.frame.origin.y;
		w = self.textLabel.frame.size.width;
		h = self.textLabel.frame.size.height;

		CGContextAddArc(context, x, y + h / 2, h / 2, M_PI / 2, 3 * M_PI / 2, 0);
		CGContextAddArc(context, x + w, y + h / 2, h / 2, 3 * M_PI / 2, M_PI / 2, 0);
		CGContextClosePath(context);
		CGContextFillPath(context);

		CGContextRestoreGState(context);
	}
	
	[super drawRect:rect];
}

@end
