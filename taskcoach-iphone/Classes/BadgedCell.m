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
		{
			bgImage = [[UIImage imageNamed:@"leather.png"] retain];
			checkImage = [[UIImage imageNamed:@"check.png"] retain];
		}
	}

	return self;
}

- (void)dealloc
{
	[bgImage release];
	[checkImage release];

	self.badge = nil;
	self.textLabel = nil;

	[super dealloc];
}

- (void)setChecked:(BOOL)checked
{
	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
		isChecked = checked;
	else
		self.accessoryType = checked ? UITableViewCellAccessoryCheckmark : UITableViewCellAccessoryNone;
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
	CGFloat x = 0, y, w, h;

	if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad)
	{
		CGContextRef context = UIGraphicsGetCurrentContext();
		CGContextSaveGState(context);
		CGContextClipToRect(context, rect);

		CGContextDrawTiledImage(context, CGRectMake(0, 0, 64, 64), bgImage.CGImage);

		CGContextSetRGBStrokeColor(context, 0, 0, 0, 1);
		CGContextSetRGBFillColor(context, 1, 1, 1, 1);

		x = self.textLabel.frame.origin.x;
		y = self.textLabel.frame.origin.y;
		w = self.textLabel.frame.size.width;
		h = self.textLabel.frame.size.height;

		CGContextAddArc(context, x, y + h / 2, h / 2, M_PI / 2, 3 * M_PI / 2, 0);
		CGContextAddArc(context, x + w, y + h / 2, h / 2, 3 * M_PI / 2, M_PI / 2, 0);
		CGContextClosePath(context);
		CGContextFillPath(context);

		CGContextRestoreGState(context);

        [super drawRect:rect];

        if (isChecked)
        {
            CGContextRef context = UIGraphicsGetCurrentContext();
            CGContextSaveGState(context);
            CGContextClipToRect(context, rect);
            
            // WTF?
            CGContextTranslateCTM(context, x + w - 30 + 11, y + h / 2);
            CGContextRotateCTM(context, M_PI);
            CGContextScaleCTM(context, -1, 1);
            
            CGRect imgRect = CGRectMake(-11, -11, 22, 22);
            CGContextDrawImage(context, imgRect, checkImage.CGImage);
            
            CGContextRestoreGState(context);
        }
	}
    else
    {
        [super drawRect:rect];
	}
}

- (void)resize
{
	
	CGRect rect = self.contentView.frame;
	
	rect.origin.x += 20 + self.indentationLevel * self.indentationWidth;
	rect.size.width -= 20 + self.indentationLevel * self.indentationWidth;
	rect.origin.y = 6;
	rect.size.height -= 12;
	rect.size.width -= 40;
	
	if (![self.badge isEmpty])
		rect.size.width -= 60;
	
	self.textLabel.frame = rect;
}

- (void)setIndentationLevel:(NSInteger)level
{
	[super setIndentationLevel:level];

	[self resize];
}

@end
